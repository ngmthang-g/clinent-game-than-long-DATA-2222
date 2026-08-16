# Current AUTO-train tool bridge — exact integration path for MainThread Action proof

Status: **CURRENT TOOL SOURCE-INSPECTED** from `ngmthang-g/AUTO-train-thanlong` main branch. Client/runtime facts referenced here retain their own VERIFIED status; proposed code changes are implementation design until locally tested.

This document connects the frozen-client reverse knowledge to the tool that already exists. It avoids an important mistake: designing a new producer bridge from scratch when the current tool already has a game-process hook, shared-memory protocol, Unity main-thread proof and semantic read-only snapshot layer.

## 1. Current tool architecture already exists

Repo:

`ngmthang-g/AUTO-train-thanlong`

Relevant source:

- `src/common/protocol.h`
- `src/bridge/bridge.cpp`
- `src/bridge/selftest.cpp`
- `src/controller/main.cpp`.

The controller installs `ThanLongNewCoreBridge.dll` into the target game **window thread** with:

```text
SetWindowsHookExW(WH_GETMESSAGE, TlGetMessageHook, bridgeModule, game.threadId)
```

Controller/bridge communicate through a per-PID file mapping:

```text
Local\ThanLongNewCore_<PID>
```

A custom wake message is posted to the game thread:

```text
kWakeMessage = WM_APP + 0x4A1
```

and `TlGetMessageHook` calls `ProcessRequest()` when it sees that message.

This is a much better starting point than a new continuous remote-worker thread.

## 2. Protocol V1.0.7 is currently read-only

Current protocol version:

```text
0x00010007
```

Current `BridgeCommand` values:

```text
None                   = 0
ValidateNative         = 1
InspectFgMainThread    = 2
InspectUnityDispatcher = 3
ProveUnityMainThread   = 4
ReadGameSnapshot       = 5
```

Current bridge state intentionally ends at:

```text
SNAPSHOT PASS ... action game vẫn KHÓA
```

This means the existing codebase is already an appropriate foundation for adding **one isolated proof command**, rather than mixing gameplay mutations into the existing read-only commands.

## 3. Critical discovery: the current hook path already executes on the Unity main thread when validation passes

`NativeValidate()` first requires:

```text
GetCurrentThreadId() == targetWindowThreadId
```

Then `ProveUnityMainThread()` performs a much stronger managed proof.

It requires:

```text
il2cpp_thread_current() != null
```

It deliberately does **not** attach an unknown worker thread.

It then obtains:

```text
System.Threading.SynchronizationContext.Current
```

and requires its actual runtime class name to be:

```text
UnitySynchronizationContext
```

Next it reads:

```text
UnitySynchronizationContext.get_MainThreadId()
System.Threading.Thread.CurrentThread.ManagedThreadId
```

and requires:

```text
currentManagedThreadId == unityMainManagedThreadId
```

Only then does it set `ValidUnityMainThread`.

### Consequence

For the **current WH_GETMESSAGE bridge path**, once `ProveUnityMainThread` passes:

- the bridge callback is already executing on a game-owned IL2CPP managed thread;
- it is specifically the Unity managed main thread according to `UnitySynchronizationContext`;
- therefore this path should **not call `il2cpp_thread_attach` again**;
- managed object allocation/delegate construction can be attempted from this already-valid context.

`thread_attach` remains necessary only for a future producer path that truly originates on a foreign native thread.

This reduces the live Action proof risk substantially.

## 4. Why still use `MainThread.Execute(Action)` if the hook already runs on main thread?

Because hook execution occurs inside the Windows message-dispatch path, not inside the normal game Update action boundary.

Directly mutating gameplay/UI from the hook could create re-entrancy/lifecycle hazards even though the OS/managed thread identity is correct.

The cleaner architecture is:

```text
controller posts wake message
 -> WH_GETMESSAGE hook enters on Unity main thread
 -> construct legitimate managed Action
 -> MainThread.Execute(Action)
 -> hook returns immediately
 -> normal Unity frame continues
 -> MainThread.Update/DoExecuteWorks drains Action
 -> callback runs in normal Update-side dispatcher lifecycle
```

So the current hook becomes a **producer**, while the game-owned queue remains the mutation execution boundary.

## 5. Critical async rule: DO NOT enqueue and wait in the same hook request

This is the most important implementation detail discovered by comparing the current tool with the solved dispatcher.

If `ProcessRequest()` does this:

```text
MainThread.Execute(action)
while (!proofStateChanged) wait
```

it can deadlock/time out.

Why:

- `ProcessRequest()` is currently executing on Unity main thread;
- the enqueued Action is normally drained by a future `Update -> DoExecuteWorks`;
- Unity cannot reach that next Update while the WH_GETMESSAGE hook is still blocked waiting.

Therefore the CTS proof **must be asynchronous/two-phase**.

## 6. Recommended protocol V1.0.8 proof commands

Proposed new commands:

```text
BeginMainThreadActionProof = 6
PollMainThreadActionProof  = 7
CleanupMainThreadActionProof = 8
```

These numbers are a proposed tool protocol design, not frozen-client constants.

Protocol version should be bumped when the shared contract changes, e.g.:

```text
0x00010008
```

so old controller/bridge pairs fail closed instead of silently misreading shared structures.

## 7. Phase A — Begin proof

`BeginMainThreadActionProof` should:

```text
1. NativeValidate + ProveUnityMainThread.
2. Reject if another proof/action is pending.
3. Resolve corlib System.Threading.CancellationTokenSource.
4. Resolve exact zero-arg .ctor.
5. Allocate CTS with il2cpp_object_new.
6. Invoke CTS .ctor.
7. Root CTS with a strong GC handle.
8. Resolve zero-arg Cancel().
9. Resolve System.Action.
10. Allocate Action.
11. Construct Action legitimately with target=CTS and callback=Cancel MethodInfo.
12. Root Action.
13. Verify IsCancellationRequested == false.
14. Resolve MainThread.Instance.
15. Call MainThread.Execute(Action).
16. Store proof state/handles in bridge-owned per-process globals.
17. Return immediately with status ENQUEUED.
```

Do **not** wait for CTS to flip during this request.

## 8. Phase B — normal Unity frame drains the Action

After the hook returns, normal frame processing can continue.

Already-VERIFIED client chain:

```text
MainThread.Update
 -> DoExecuteWorks
 -> queue dequeue
 -> Action.Invoke
 -> CancellationTokenSource.Cancel()
```

The rooted CTS remains alive for observation.

## 9. Phase C — Poll proof

Controller waits a short interval, then sends:

```text
PollMainThreadActionProof
```

The new hook invocation can read:

```text
CTS.get_IsCancellationRequested()
```

Possible states:

```text
PENDING  -> still false, within deadline
PASS     -> true
TIMEOUT  -> still false after deadline
ERROR    -> object/handle/exception invalid
```

On PASS:

- optionally call `CTS.Dispose()`;
- free Action GC handle;
- free CTS GC handle;
- clear pending proof state;
- return a durable diagnostic result.

Do not enqueue another Action from the Poll path.

## 10. Cleanup command

`CleanupMainThreadActionProof` is useful for:

- controller disconnect;
- timeout recovery;
- user abort;
- failed intermediate construction after one handle has already been created.

Cleanup must be idempotent.

A tiny managed leak is preferable to freeing a target/action whose lifetime is uncertain. Fail closed.

## 11. Existing `Il2CppApi` delta

Current `bridge.cpp` resolves 30 read/query exports but lacks several construction/lifetime APIs needed for the proof.

Add at minimum:

```text
il2cpp_object_new
il2cpp_gchandle_new
il2cpp_gchandle_get_target
il2cpp_gchandle_free
```

Optional/future producer-thread support:

```text
il2cpp_thread_attach
il2cpp_thread_detach
```

For the current validated WH_GETMESSAGE path, do not attach if `thread_current()` already proves the hook is a managed Unity thread.

The current resolver already has many useful pieces:

- get_corlib
- class_from_name
- class_get_method_from_name
- class_get_methods
- method_get_param_count
- method_get_param
- method_get_return_type
- method_get_flags
- runtime_invoke
- object_get_class
- object_unbox
- class/field helpers.

So the required code delta is much smaller than a new bridge implementation.

## 12. MainThread.Instance resolution in current bridge

Use the already-known class:

```text
FGStudio.Engine.Utilities.MainThread
```

Resolve:

```text
get_Instance()
```

and invoke it on the already-proven Unity managed hook thread.

Require non-null before Action construction/enqueue is considered usable.

Do not read the static backing field by guessed address when a semantic getter exists.

## 13. `System.Action` construction in this tool

Canonical evidence is in `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

Frozen generated constructor ABI:

```text
RCX = Action object
RDX = target object or null
R8  = callback MethodInfo*
R9  = null
```

Best implementation order for this fixed client:

1. resolve Action semantically;
2. allocate Action through `il2cpp_object_new`;
3. resolve CTS.Cancel MethodInfo semantically;
4. use the verified legitimate constructor path;
5. never fill delegate offsets manually.

If a pure managed `runtime_invoke`/reflection delegate-construction path is proven later, it may replace frozen native-constructor address usage. Until then, the direct generated donor ABI is the strongest snapshot-specific evidence.

## 14. Suggested proof state object inside bridge

Bridge-local per-process globals are sufficient because the DLL instance lives inside one game process.

Conceptual structure:

```text
ActionProofState {
    bool active
    uint32 generation
    uint32 targetHandle
    uint32 actionHandle
    Il2CppObject* targetCachedForDiagnostics
    uint64 beginTick
    uint64 deadlineTick
    ProofStage stage
    int errorCode
}
```

Prefer retrieving target from `gchandle_get_target` during Poll instead of trusting a stale cached raw pointer.

## 15. Shared response extension

Add a compact proof snapshot rather than writing proof data into free-form text only.

Example:

```text
ActionProofSnapshot {
    uint32 validMask
    uint32 generation
    int32 state        // Idle/Enqueued/Pending/Pass/Timeout/Error
    int32 stage
    int32 errorCode
    uint32 callbackObserved
    uint64 durationMs
}
```

The controller can still display Vietnamese detail text for humans.

## 16. Controller state-machine integration

Current controller already guarantees only one outstanding bridge command:

```text
if (Busy()) -> reject
pending_ != None -> fail invariant
```

Preserve that.

Add states such as:

```text
ActionProofStarting
ActionProofWaitingFrame
ActionProofPolling
ActionProofPassed
```

Recommended flow:

```text
SnapshotReady
 -> user/test initiates proof
 -> Begin command
 -> ENQUEUED response
 -> controller waits >= one timer interval without blocking game thread
 -> Poll command
 -> Pending: wait and poll later
 -> Pass: mark bridge action path proven
 -> Timeout/Error: fail closed, cleanup
```

Never spam Poll every message/frame. 50–200 ms polling is enough for a proof; exact interval is tool policy.

## 17. Current `selftest.cpp` is not a runtime Action proof

Current bridge selftest only:

- loads the DLL locally;
- confirms `TlGetMessageHook` export exists;
- prints `BRIDGE SELFTEST PASS`.

Keep it for packaging/export validation, but do not confuse it with the in-game MainThread proof.

The CTS proof belongs to the live controller/bridge protocol.

## 18. Safety of first test

CTS proof is deliberately chosen because it changes only an isolated BCL object created by the bridge.

It does not:

- send a packet;
- move the player;
- choose a target;
- alter UI state;
- change inventory;
- revive;
- interact with party/social systems.

This is a better first mutable managed callback than any gameplay action.

## 19. After CTS PASS

Do not immediately enable every feature.

Promotion order:

```text
CTS managed proof
 -> low-risk semantic Game/Lua action with clear state proof
 -> movement/target/skill
 -> transactional shop/item/team actions
```

At each step, preserve max one mutable action per PID.

## 20. Architectural conclusion

The current tool is already much closer to the target architecture than a fresh bridge would be:

```text
External controller
 -> per-PID shared mapping
 -> WH_GETMESSAGE producer hook
 -> PROVEN Unity managed main thread
 -> legitimate managed Action
 -> MainThread.Execute
 -> game-owned ConcurrentQueue<Action>
 -> Unity Update
 -> semantic action
 -> observer/state proof
```

The next implementation task is therefore **not “invent injection/main-thread control.”** It is a small, isolated extension of the current read-only protocol to construct/root/enqueue one legitimate Action asynchronously and prove it with CTS.