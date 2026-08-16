# Build Contract — `MAINTHREAD_BRIDGE_V1`

Purpose: give future tool-building AI a **small implementation contract** so it does not need to reread all native reverse documents before coding.

Current-tool integration is documented in:

- `analysis/31_CURRENT_AUTO_TOOL_BRIDGE_INTEGRATION.md`.

Read deeper client evidence only if this contract is insufficient:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

## 1. Non-negotiable architecture

For the current `AUTO-train-thanlong` tool:

```text
External controller
 -> per-PID shared mapping
 -> PostThreadMessage(kWakeMessage)
 -> WH_GETMESSAGE TlGetMessageHook
 -> validated Unity managed main thread
 -> construct legitimate System.Action
 -> FGStudio.Engine.Utilities.MainThread.Execute(Action)
 -> ConcurrentQueue<Action>
 -> hook returns
 -> later Unity Update
 -> DoExecuteWorks
 -> Action.Invoke
 -> observer/state proof
```

Do not expose a production primitive that directly invokes arbitrary Game/Lua/UI mutation from the hook callback merely because the hook already runs on the correct thread. Queueing avoids Windows-message-hook re-entrancy and restores the game-owned Update execution boundary.

## 2. Current tool fact: producer thread is already managed Unity main thread when proof passes

The current bridge source performs all of these checks before setting `ValidUnityMainThread`:

```text
GetCurrentThreadId() == targetWindowThreadId
il2cpp_thread_current() != null
SynchronizationContext.Current is UnitySynchronizationContext
CurrentThread.ManagedThreadId == UnitySynchronizationContext.MainThreadId
```

Therefore the current WH_GETMESSAGE producer path should **not** call `il2cpp_thread_attach` after this proof passes.

Use `thread_attach` only for a genuinely foreign future producer context.

## 3. Existing protocol must be extended, not replaced

Current protocol V1.0.7 already provides one-command-at-a-time shared-memory request/response and commands 1..5 for read-only validation/snapshot.

Recommended V1.0.8 additions:

```text
BeginMainThreadActionProof   = 6
PollMainThreadActionProof    = 7
CleanupMainThreadActionProof = 8
```

Bump protocol version when request/response structures change so mismatched controller/bridge binaries fail closed.

## 4. Critical async rule

**Never enqueue an Action and synchronously wait for its callback inside the same WH_GETMESSAGE hook request.**

That would block the Unity main thread and prevent the future `Update()` that drains the queue.

The proof must be two-phase:

```text
Begin -> construct/root/enqueue -> return from hook
        [normal Unity Update invokes Action]
Poll  -> observe callback state -> cleanup/pass
```

This rule is mandatory for the current tool architecture.

## 5. Minimal bridge interface

At the controller/state-machine level:

```text
BridgeResolve(pid) -> BridgeContext
BridgeProbeMainThread(ctx) -> MainThreadStatus
BridgeBeginCtsProof(ctx) -> Enqueued/Pending/Error
BridgePollCtsProof(ctx) -> Pending/Pass/Timeout/Error
BridgeCleanupCtsProof(ctx)
BridgeEnqueueAction(ctx, ManagedActionDescriptor) -> EnqueueResult   // only after proof is promoted
BridgeRelease(ctx)
```

Do **not** start with a giant generic remote invocation API.

## 6. `BridgeContext`

Per PID only:

```text
ProcessId
GameAssemblyBase
ResolvedExports
Il2CppDomain
ProducerThreadAttachState
MainThreadClass
MainThreadInstance
ActionClass
ActionProofGeneration
ActionProofState
LastException
LastErrorCode
```

Never share live pointers/GC handles between game processes.

## 7. `ManagedActionDescriptor`

```text
TargetObject        // nullable for static callback
CallbackMethodInfo  // required
ExpectedParamCount = 0
ExpectedReturnType  = System.Void
DebugName
```

The V1 bridge accepts only callbacks compatible with `System.Action`:

- zero managed arguments;
- void return.

Reject incompatible callbacks before constructing the delegate.

## 8. Resolver rules

Resolve by names/metadata whenever possible:

```text
FGStudio.Engine.Utilities.MainThread
System.Action
System.Threading.CancellationTokenSource
```

Use exported IL2CPP APIs for assembly/image/class/method lookup.

Historic RVAs/tokens are frozen-snapshot diagnostics, not the sole production identity.

## 9. Required new IL2CPP API delta for current `bridge.cpp`

Current bridge already resolves the read/query APIs needed for metadata and `runtime_invoke`.

Add at minimum:

```text
il2cpp_object_new
il2cpp_gchandle_new
il2cpp_gchandle_get_target
il2cpp_gchandle_free
```

Keep optional support for:

```text
il2cpp_thread_attach
il2cpp_thread_detach
```

but do not attach the existing validated hook thread again.

## 10. Action construction

Verified generated donor ABI in this frozen client:

```text
ActionCtor(
    actionObject,
    targetObjectOrNull,
    callbackMethodInfo,
    null
)
```

The bridge must use a legitimate delegate construction path.

Forbidden:

```text
allocate raw bytes
write guessed fields
pretend result is System.Action
```

## 11. GC ownership

V1 proof policy:

```text
Begin request:
  root target
  root Action
  enqueue
  return

Poll request(s):
  recover target through strong GC handle
  inspect state

Pass/cleanup:
  release Action root
  release target root
```

Use strong `il2cpp_gchandle_new(..., false)` handles.

Do not free a target root before proof if the Poll phase still needs to inspect it.

## 12. Canonical proof target

Use:

```text
System.Threading.CancellationTokenSource
```

Frozen metadata cross-check:

```text
zero-arg .ctor token = 0x0600120A
zero-arg Cancel token = 0x0600120B
get_IsCancellationRequested token = 0x06001203
```

Runtime code should resolve semantically and use these only as diagnostics/cross-checks.

## 13. Begin proof contract

`BridgeBeginCtsProof`:

```text
require ValidUnityMainThread
require no active proof/action
resolve/allocate CTS
invoke zero-arg CTS .ctor
root CTS
resolve zero-arg Cancel [void]
resolve/allocate System.Action
construct legitimate Action(target=CTS, callback=Cancel)
root Action
verify CTS cancellation state == false
resolve non-null MainThread.Instance
invoke MainThread.Execute(Action)
store proof generation + handles + begin/deadline time
return ENQUEUED immediately
```

Do not poll CTS before returning from the same hook invocation.

## 14. Poll proof contract

`BridgePollCtsProof`:

```text
require active proof
recover CTS from target GC handle
read get_IsCancellationRequested
if true:
    mark PASS
    optional Dispose
    cleanup handles
    return PASS
if deadline exceeded:
    return TIMEOUT / cleanup according to fail-closed policy
otherwise:
    return PENDING
```

Poll must not enqueue another callback.

Controller policy should poll at a modest interval such as 50–200 ms rather than spam the game message queue.

## 15. Proof result

Add a structured result, e.g.:

```text
ActionProofSnapshot {
  ValidMask
  Generation
  State       // Idle/Enqueued/Pending/Pass/Timeout/Error
  Stage
  ErrorCode
  CallbackObserved
  DurationMs
}
```

Human-readable `detail` remains useful, but automation must not parse free-form text as state.

Optional diagnostics:

```text
ProducerTID
ObservedUnityManagedThreadId
CallbackTID
```

Direct callback TID measurement is optional because the static queue consumer is already VERIFIED to invoke from Unity Update.

## 16. Error codes

Canonical V1 codes:

```text
OK
GAMEASSEMBLY_NOT_FOUND
EXPORT_RESOLVE_FAIL
DOMAIN_RESOLVE_FAIL
HOOK_NOT_UNITY_MAINTHREAD
MAINTHREAD_CLASS_FAIL
MAINTHREAD_INSTANCE_NULL
ACTION_CLASS_FAIL
TARGET_CLASS_FAIL
TARGET_ALLOC_FAIL
TARGET_CTOR_FAIL
CALLBACK_METHOD_FAIL
CALLBACK_SIGNATURE_MISMATCH
ACTION_ALLOC_FAIL
ACTION_CTOR_FAIL
TARGET_GCHANDLE_FAIL
ACTION_GCHANDLE_FAIL
EXECUTE_METHOD_FAIL
EXECUTE_EXCEPTION
PROOF_ALREADY_ACTIVE
PROOF_NOT_ACTIVE
CALLBACK_TIMEOUT
TARGET_STATE_UNCHANGED
GC_LIFETIME_ERROR
PROCESS_EXITED
```

The UI/log should display the specific stage instead of only `Bridge failed`.

## 17. Mutable action gate

After the proof is VERIFIED, each PID still gets:

```text
maxPendingMutableActions = 1
```

Higher feature layers wait for semantic state proof before enqueuing another mutation.

Read-only scanners are separate and may run concurrently.

## 18. First gameplay promotion ladder

Do not jump from CTS proof directly to Auto Sell/Revive.

Recommended promotion:

```text
Stage 0: CTS isolated managed proof
Stage 1: harmless/cosmetic semantic callback if available
Stage 2: low-risk reversible gameplay semantic action
Stage 3: movement/target/skill actions
Stage 4: transactional item/shop/social actions
```

Every stage must record expected state proof and timeout behavior.

## 19. Definition of done for V1

`MAINTHREAD_BRIDGE_V1` is complete when, for one live game PID:

1. existing main-thread validator passes;
2. resolver finds non-null MainThread.Instance;
3. CTS target is allocated/initialized/rooted;
4. legitimate Action is constructed/rooted;
5. Begin command enqueues and returns without blocking Unity;
6. a later Poll observes CTS state false -> true;
7. repeated proofs do not crash/corrupt GC;
8. cleanup releases roots safely;
9. diagnostics distinguish every failure stage;
10. protocol/controller enforce at most one pending proof/mutable action.

Only then should feature-specific action contracts depend on this bridge.