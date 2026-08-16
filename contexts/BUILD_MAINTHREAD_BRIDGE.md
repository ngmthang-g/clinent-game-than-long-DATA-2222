# Context Pack — Build MainThread Bridge

## Scope

Use when implementing or debugging the external bridge that must execute semantic Game/Lua/UI work on Unity's main thread.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/21_MAIN_THREAD_DISPATCHER.md`
3. `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
4. `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`
5. `analysis/01_IL2CPP_RUNTIME_METADATA.md`
6. `research/TODO.md`

## VERIFIED internal chain

`MainThread.Execute(System.Action)` is not speculative.

Frozen client truth:

- `MainThread.Instance` is established in `Awake()`;
- queue field is `ConcurrentQueue<System.Action>` at instance offset `+0x20` in this snapshot;
- `Execute(Action)` enqueues;
- `Update()` calls `DoExecuteWorks()`;
- `DoExecuteWorks()` dequeues and invokes Actions until empty;
- `TCPGame`/`TCPLogin` producer handlers create legitimate managed Actions and call `MainThread.Execute`.

## VERIFIED Action-construction details

Direct frozen GameAssembly disassembly also proves the generated `System.Action` constructor pattern used by the client:

```text
RCX = new Action object
RDX = managed target object, or null for static callback
R8  = callback MethodInfo*
R9  = null in observed generated call sites
```

The constructor initializes real delegate runtime fields and performs managed-reference write-barrier handling. Null-target/static Action construction is also present in shipped call sites.

Do **not** forge delegate memory manually.

## Required IL2CPP producer capabilities are exported

Relevant exported APIs include semantic class/method/type resolution, `il2cpp_object_new`, `il2cpp_runtime_invoke`, `il2cpp_thread_attach/detach` and strong `il2cpp_gchandle_*` rooting.

Therefore the bridge should resolve objects/methods semantically and use historic RVAs only as frozen-snapshot evidence/debug hints.

## Remaining narrow problem

External code still must prove:

1. resolve non-null `MainThread.Instance` per PID;
2. attach producer context to IL2CPP if it is not already attached;
3. allocate/initialize a legitimate managed target;
4. construct a legitimate `System.Action` from target + callback MethodInfo;
5. root managed objects safely across enqueue/execution;
6. enqueue through `MainThread.Execute`;
7. observe a harmless callback result;
8. verify no exception/crash/GC corruption.

## Canonical first live proof

Use an isolated BCL object instead of game state:

```text
System.Threading.CancellationTokenSource
```

Build an Action targeting its parameterless `Cancel()` method.

Expected state proof:

```text
IsCancellationRequested == false
   -> enqueue Action through MainThread.Execute
   -> Unity Update drains Action
   -> IsCancellationRequested == true
```

Before binding, resolve the exact `Cancel` overload and verify zero parameters + `System.Void` return.

This proof does not move the player, touch UI, send packets, mutate items or alter social state.

Full recipe: `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

## GC/lifetime rule

Use strong GC handles during the proof.

At minimum:

- root the CancellationTokenSource until its state transition has been observed;
- root Action through enqueue; retaining it until proof completion is acceptable for the first test;
- free roots only after success/timeout cleanup is safe.

Once an Action is successfully stored in the managed `ConcurrentQueue<Action>`, the queue itself owns a strong reference to it.

## Invocation rule

`il2cpp_runtime_invoke` is only an invocation primitive. It does not make arbitrary gameplay calls thread-safe.

It may be used from a valid attached producer context for bridge operations or `MainThread.Execute`, because Execute only enqueues into the game-owned concurrent queue.

Gameplay mutations still execute inside the queued Action on Unity Update.

## Optional direct TID diagnostic

The CTS false->true transition plus the already-VERIFIED static chain `Update -> DoExecuteWorks -> Action.Invoke` is sufficient as the primary end-to-end bridge proof.

If direct TID equality is desired, use a diagnostic-only one-shot observation and record producer TID / callback TID / Unity Update TID. Do not add a permanent gameplay hook just for this.

## Failure codes worth preserving

```text
DOMAIN_RESOLVE_FAIL
THREAD_ATTACH_FAIL
MAINTHREAD_INSTANCE_NULL
TARGET_CLASS_FAIL
TARGET_CTOR_FAIL
CALLBACK_METHOD_FAIL
ACTION_ALLOC_FAIL
ACTION_CTOR_FAIL
GCHANDLE_FAIL
EXECUTE_EXCEPTION
CALLBACK_TIMEOUT
TARGET_STATE_UNCHANGED
GC_LIFETIME_ERROR
```

## Do not regress to

- direct arbitrary-thread `Game.GoTo`, `UseSkill`, `ClickNPC`, Lua UI calls;
- production CreateRemoteThread gameplay worker;
- fake delegate memory layouts;
- Sell/Abandon/Revive/party mutation as first bridge proof.

## Completion criteria

Promote the external bridge to VERIFIED only after a legitimately constructed Action is queued and its isolated managed callback state is observed changing without lifetime/GC corruption. After that, test one low-risk semantic game action before migrating feature mutations.