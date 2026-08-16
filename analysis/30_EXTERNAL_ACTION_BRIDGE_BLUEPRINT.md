# External `System.Action` bridge — exact construction blueprint

Status: **native delegate-construction ABI VERIFIED from frozen GameAssembly; full external live enqueue proof still pending.**

This document narrows the remaining MainThread problem to a concrete producer-side implementation recipe. The consumer side is already solved in `analysis/21_MAIN_THREAD_DISPATCHER.md` and the game-owned producer pattern is documented in `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`.

## 1. New direct finding: `System.Action` constructor ABI

Direct frozen `GameAssembly.dll` disassembly resolves the generated `System.Action` delegate constructor used by the game's own producers at:

- RVA `0x49F810`
- VA `0x18049F810` in the frozen image.

Observed Windows x64 call shape from the shipped `TCPGame.SocketCommandHandler` producer:

```text
RCX = newly allocated System.Action object
RDX = managed delegate target object / closure
R8  = callback MethodInfo*
R9  = null in observed generated call sites
call System.Action::.ctor
```

This is not inferred from C# syntax; it is the exact argument pattern emitted by this client.

## 2. Delegate constructor fields observed

The constructor does not treat Action as a tiny unmanaged callback struct. It initializes managed delegate internals.

Observed stores include:

```text
Action + 0x10 <- [callback MethodInfo + 0x08]
Action + 0x20 <- target object
Action + 0x28 <- callback MethodInfo*
Action + 0x40 <- delegate target/self-related runtime field
```

It also computes/stores delegate invocation/trampoline fields around `+0x18` / `+0x38` and invokes the IL2CPP managed-reference write barrier after assigning the target.

Conclusion:

**Do not forge Action by copying these offsets manually.** The safe donor is the legitimate constructor path.

Historic offsets are evidence for this fixed snapshot, not a recommendation to hand-build a delegate layout.

## 3. Static target (`target == null`) is supported by the shipped constructor path

Direct GameAssembly call sites exist where the game allocates a `System.Action` and invokes the same constructor with:

```text
RDX = 0
R8  = callback MethodInfo*
```

For example, call sites around `0x1806BC960` and `0x1806BC983` construct Action delegates with a null target.

Therefore the constructor supports both:

- instance callback: managed target + MethodInfo;
- static callback: null target + MethodInfo.

This is useful for harmless proof callbacks and reduces the need to manufacture a closure when no captured state is required.

## 4. IL2CPP exports needed by the external producer are present

The frozen `GameAssembly.dll` export surface includes the APIs needed for semantic runtime construction/resolution, including:

- `il2cpp_domain_get`
- `il2cpp_domain_get_assemblies`
- `il2cpp_assembly_get_image`
- `il2cpp_class_from_name`
- `il2cpp_class_get_method_from_name`
- `il2cpp_class_get_methods`
- `il2cpp_method_get_param_count`
- `il2cpp_method_get_param`
- `il2cpp_method_get_return_type`
- `il2cpp_method_get_flags`
- `il2cpp_type_get_name`
- `il2cpp_class_get_type`
- `il2cpp_type_get_object`
- `il2cpp_method_get_object`
- `il2cpp_object_new`
- `il2cpp_runtime_invoke`
- `il2cpp_thread_attach`
- `il2cpp_thread_detach`
- `il2cpp_gchandle_new`
- `il2cpp_gchandle_get_target`
- `il2cpp_gchandle_free`
- `il2cpp_class_get_field_from_name`
- `il2cpp_field_get_value`
- `il2cpp_property_get_get_method`.

This means the bridge can be semantic/resolver-driven instead of depending only on historic RVAs.

## 5. Producer-thread attachment rule

If the producer execution context is not already an IL2CPP-attached managed runtime thread, attach before allocating/invoking managed objects:

```text
domain = il2cpp_domain_get()
il2cpp_thread_attach(domain)
```

Detach only when that producer context is truly finished and the bridge architecture permits it.

Do not assume a native thread created/injected externally is automatically a valid IL2CPP managed thread.

## 6. Strong GC rooting is available

The client exports strong GC-handle APIs.

Recommended rule during the proof:

```text
targetHandle = il2cpp_gchandle_new(target, false)
actionHandle = il2cpp_gchandle_new(action, false)
```

Keep the proof target rooted until the external observer has verified the callback result.

Keep Action rooted at least through successful enqueue. Once `MainThread.Execute` has stored the Action in `ConcurrentQueue<Action>`, the queue itself is a managed strong reference; the external Action handle can then be released if desired. During the first proof, retaining both handles until completion is simpler and safer.

## 7. Best first proof callback: isolated `CancellationTokenSource.Cancel()`

A better proof than movement/UI/gameplay is a completely isolated BCL managed object.

The frozen metadata contains:

- `System.Threading.CancellationTokenSource`
- `Cancel`
- `IsCancellationRequested`.

Recommended proof object:

```text
new System.Threading.CancellationTokenSource()
```

Recommended Action target/method:

```text
target = CancellationTokenSource instance
callback = CancellationTokenSource.Cancel()   // parameterless instance method
```

Expected observable state:

```text
IsCancellationRequested: false -> true
```

Why this is a strong first test:

- no game state mutation;
- no Unity object mutation;
- no network packet;
- no item/social/destructive action;
- callback result is externally observable by reading a managed property;
- object can be rooted independently until proof completes.

Before using it, resolve the exact overload and verify:

- method name `Cancel`;
- parameter count `0`;
- return type `System.Void`;
- instance/static flags match the intended target form.

Do not blindly bind only by name if overload ambiguity exists.

## 8. Recommended proof algorithm

Per PID:

```text
1. Resolve IL2CPP exports.
2. Attach producer context to IL2CPP if needed.
3. Resolve MainThread class + non-null MainThread.Instance.
4. Resolve System.Action class.
5. Resolve System.Threading.CancellationTokenSource class.
6. Allocate CTS object and run its parameterless constructor through a valid managed invocation path.
7. Strong-root CTS.
8. Resolve CTS.Cancel() and verify zero-arg void instance signature.
9. Allocate System.Action object.
10. Construct Action legitimately with target=CTS and callback MethodInfo=Cancel.
11. Strong-root Action.
12. Confirm CTS.IsCancellationRequested == false.
13. Invoke MainThread.Execute(Action) from the producer context.
14. Poll/read CTS.IsCancellationRequested without issuing another mutable game action.
15. Success when it becomes true.
16. Record enqueue/proof timing and bridge diagnostics.
17. Release Action/CTS GC handles after proof cleanup.
```

The game-owned queue consumer already proves that an Action dequeued by `DoExecuteWorks()` is invoked from Unity `Update()`. Therefore an isolated false->true CTS transition after enqueue is a practical end-to-end proof that the external bridge successfully constructed a valid managed delegate and crossed the MainThread queue boundary.

## 9. Optional direct thread-ID proof

If direct TID equality is still desired after the CTS proof, add a **diagnostic-only** one-shot observation layer around the queued callback or `DoExecuteWorks` and record `GetCurrentThreadId()`.

Do not make a permanent gameplay hook merely to prove something the static consumer disassembly already establishes.

Operational acceptance can be:

```text
valid managed Action constructed
+ Execute accepts/enqueues it
+ isolated callback state changes
+ no exception/crash/GC corruption
```

with static `Update -> DoExecuteWorks -> Action.Invoke` evidence supplying the execution-thread semantics.

## 10. `runtime_invoke` boundary

`il2cpp_runtime_invoke` may be used from a correctly attached producer context for runtime-safe bridge/resolver operations and for `MainThread.Execute`, because `Execute` itself only crosses the thread-safe queue boundary.

Do **not** reinterpret this as permission to call gameplay mutations (`Game.GoTo`, skill use, Lua UI actions, etc.) directly from that producer thread.

Gameplay mutations still belong inside the queued Action on Unity Update.

## 11. Two legitimate Action-construction strategies

### Strategy A — exact generated constructor ABI

- resolve `System.Action` class;
- allocate with `il2cpp_object_new`;
- resolve callback `MethodInfo*` semantically;
- invoke the legitimate generated Action constructor using the verified target + MethodInfo ABI;
- root through GC handle;
- enqueue.

This is closest to the game's own native producer pattern.

### Strategy B — managed `Delegate.CreateDelegate`

The frozen metadata contains `CreateDelegate`, and IL2CPP exposes reflection objects (`il2cpp_type_get_object`, `il2cpp_method_get_object`). A bridge may enumerate `System.Delegate.CreateDelegate` overloads, verify parameter types, and construct an Action through managed reflection.

This can reduce dependency on delegate native layout, but the exact chosen overload must be resolved and tested at runtime rather than guessed.

For the frozen client, Strategy A currently has the strongest direct native donor evidence.

## 12. Failure diagnostics

Record explicit failure stages:

```text
DOMAIN_RESOLVE_FAIL
THREAD_ATTACH_FAIL
MAINTHREAD_INSTANCE_NULL
CTS_CLASS_FAIL
CTS_CTOR_FAIL
CALLBACK_METHOD_FAIL
ACTION_CLASS_FAIL
ACTION_ALLOC_FAIL
ACTION_CTOR_FAIL
GCHANDLE_FAIL
EXECUTE_EXCEPTION
CALLBACK_TIMEOUT
CTS_STATE_UNCHANGED
GC_LIFETIME_ERROR
```

Do not collapse them into “MainThread failed”.

## 13. Promotion rule

After one CTS Action succeeds repeatedly without corruption:

- mark external managed Action construction as runtime VERIFIED;
- preserve the exact construction/rooting strategy in the KB;
- then perform one low-risk semantic game action;
- only after that migrate Auto Train/Buff/Sell/Heal/Revive mutable actions to the bridge.

Do not start with Sell, Abandon, Revive, party mutation or map travel.

## 14. What future AI must not redo

Do not re-reverse:

- whether `MainThread.Execute` enqueues;
- whether Update drains the queue;
- whether Action constructor supports target + callback MethodInfo;
- whether null/static targets are possible;
- whether the required IL2CPP GC-handle/object/reflection exports exist.

Those are now recorded from direct frozen-client evidence. The only missing part is the **live external construction/enqueue proof**.