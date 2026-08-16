# Build Contract — `MAINTHREAD_BRIDGE_V1`

Purpose: give future tool-building AI a **small implementation contract** so it does not need to reread all native reverse documents before coding.

Read deeper evidence only if this contract is insufficient:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

## 1. Non-negotiable architecture

The external controller may resolve/read state from its producer context, but gameplay/UI mutations must be marshalled through:

```text
valid managed System.Action
 -> FGStudio.Engine.Utilities.MainThread.Execute(Action)
 -> ConcurrentQueue<Action>
 -> Unity Update
 -> DoExecuteWorks
 -> Action.Invoke
```

Do not expose a production primitive that directly invokes arbitrary Game/Lua/UI mutation on the producer thread.

## 2. Minimal public bridge interface

Recommended first interface:

```text
BridgeResolve(pid) -> BridgeContext
BridgeProbeMainThread(ctx) -> MainThreadStatus
BridgeRunCtsProof(ctx) -> ProofResult
BridgeEnqueueAction(ctx, ManagedActionDescriptor) -> EnqueueResult
BridgeRelease(ctx)
```

Do **not** start with a giant generic remote invocation API.

## 3. `BridgeContext`

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
LastException
LastErrorCode
```

Never share live pointers between game processes.

## 4. `ManagedActionDescriptor`

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

## 5. Resolver rules

Resolve by names/metadata whenever possible:

```text
FGStudio.Engine.Utilities.MainThread
System.Action
System.Threading.CancellationTokenSource
```

Use exported IL2CPP APIs for assembly/image/class/method lookup.

Historic RVAs are frozen-snapshot diagnostics, not the sole identity.

## 6. Producer thread

Before managed allocation/invoke:

```text
if producer context is not attached:
    domain = il2cpp_domain_get()
    il2cpp_thread_attach(domain)
```

Record whether the bridge attached the thread itself so cleanup does not detach an unrelated game-owned managed thread.

## 7. Action construction

Verified generated donor ABI in this snapshot:

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

## 8. GC ownership

V1 proof policy:

```text
root target
root Action
construct/enqueue
wait proof
release Action root
release target root
```

Use strong `il2cpp_gchandle_new(..., false)` handles.

Do not free a target root before proof if the external observer still needs to inspect it.

## 9. Canonical proof

`BridgeRunCtsProof` should use:

```text
System.Threading.CancellationTokenSource
```

Sequence:

```text
allocate + initialize CTS
root CTS
resolve Cancel() [0 args, void]
construct rooted Action(target=CTS, callback=Cancel)
assert IsCancellationRequested == false
enqueue Action
wait until IsCancellationRequested == true
cleanup roots
```

This proof must not:

- move the role;
- interact with NPC/UI;
- send game packets;
- alter items;
- alter team/social state.

## 10. Proof result

```text
ProofResult {
  Success
  ErrorCode
  Stage
  MainThreadInstance
  TargetHandleCreated
  ActionHandleCreated
  EnqueueReturned
  CallbackObserved
  DurationMs
  ExceptionPointerOrMessage
}
```

Optional diagnostics:

```text
ProducerTID
ObservedUnityTID
CallbackTID
```

Direct TID measurement is optional once the isolated callback result is observed, because the static queue consumer is already VERIFIED to invoke from Unity Update.

## 11. Error codes

Canonical V1 codes:

```text
OK
GAMEASSEMBLY_NOT_FOUND
EXPORT_RESOLVE_FAIL
DOMAIN_RESOLVE_FAIL
THREAD_ATTACH_FAIL
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
CALLBACK_TIMEOUT
TARGET_STATE_UNCHANGED
GC_LIFETIME_ERROR
PROCESS_EXITED
```

The UI/log should display the specific stage instead of only `Bridge failed`.

## 12. Mutable action gate

After the proof is VERIFIED, each PID still gets:

```text
maxPendingMutableActions = 1
```

Higher feature layers wait for semantic state proof before enqueuing another mutation.

Read-only scanners are separate and may run concurrently.

## 13. First gameplay promotion ladder

Do not jump from CTS proof directly to Auto Sell/Revive.

Recommended promotion:

```text
Stage 0: CTS isolated managed proof
Stage 1: harmless/read-only or cosmetic semantic callback if available
Stage 2: low-risk reversible gameplay semantic action
Stage 3: movement/target/skill actions
Stage 4: transactional item/shop/social actions
```

Every stage must record expected state proof and timeout behavior.

## 14. Definition of done for V1

`MAINTHREAD_BRIDGE_V1` is complete when, for one live game PID:

1. resolver finds MainThread Instance;
2. producer is correctly attached to IL2CPP;
3. CTS target is allocated/initialized/rooted;
4. legitimate Action is constructed/rooted;
5. `Execute(Action)` accepts it without managed exception;
6. CTS state changes from false to true;
7. repeated proofs do not crash/corrupt GC;
8. cleanup releases roots safely;
9. diagnostics distinguish every failure stage.

Only then should feature-specific action contracts depend on this bridge.