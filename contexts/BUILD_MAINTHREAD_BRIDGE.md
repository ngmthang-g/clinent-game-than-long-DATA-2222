# Context Pack — Build MainThread Bridge

## Scope

Use when implementing or debugging the external bridge that must execute semantic Game/Lua/UI work on Unity's main thread.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/21_MAIN_THREAD_DISPATCHER.md`
3. `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
4. `analysis/01_IL2CPP_RUNTIME_METADATA.md`
5. `research/TODO.md`

## VERIFIED internal chain

`MainThread.Execute(System.Action)` is not speculative.

Frozen client truth:

- `MainThread.Instance` is established in `Awake()`;
- queue field is `ConcurrentQueue<System.Action>` at instance offset `+0x20` in this snapshot;
- `Execute(Action)` enqueues;
- `Update()` calls `DoExecuteWorks()`;
- `DoExecuteWorks()` dequeues and invokes Actions until empty;
- `TCPGame`/`TCPLogin` producer handlers create legitimate managed Actions and call `MainThread.Execute`.

## Remaining narrow problem

External code still must prove:

1. resolve non-null `MainThread.Instance` per PID;
2. allocate/root a legitimate managed target/delegate or reuse a compatible managed producer path;
3. construct a valid `System.Action` using managed/IL2CPP semantics, not a forged unmanaged struct;
4. enqueue it;
5. keep target/delegate alive across enqueue -> next Unity Update;
6. verify callback thread ID equals Unity Update thread ID;
7. verify no GC/lifetime corruption.

## First live proof

Use a harmless callback. Do not use Sell, Abandon Item, Revive, movement or destructive/social mutation as the first test.

Record:

- producer TID;
- Unity Update TID;
- callback TID;
- delegate allocation/root strategy;
- enqueue result;
- callback count;
- any exception/crash/no-op.

## Delegate construction rule

The shipped producer donor demonstrates:

`managed closure allocation -> capture assignment + GC write barrier -> new System.Action -> Action::.ctor(target, callback) -> MainThread.Execute(action)`.

Do not manually copy a few delegate fields and call it a `System.Action`.

## Invocation rule

`il2cpp_runtime_invoke` is only an invocation primitive. It does not make arbitrary gameplay calls thread-safe.

It may be useful to invoke safe resolver/bridge operations or `MainThread.Execute`, but gameplay mutation itself should execute from the queued Action on Unity Update.

## Lifetime rules

- never share Action/target/MainThread pointers across PIDs;
- re-resolve after game restart;
- root managed objects until callback completion;
- release roots only after proof callback executed or timeout cleanup is safe;
- keep max one mutable external Action pending per PID.

## Do not regress to

- direct arbitrary-thread `Game.GoTo`, `UseSkill`, `ClickNPC`, Lua UI calls;
- production CreateRemoteThread gameplay worker;
- fake delegate memory layouts without GC/runtime semantics.

## Completion criteria

Promote external bridge to VERIFIED only after one harmless Action is constructed, queued and observed executing on the Unity Update TID without lifetime/GC corruption. Then use the same bridge for semantic feature actions.