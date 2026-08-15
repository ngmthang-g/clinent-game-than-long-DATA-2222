# FGStudio MainThread dispatcher — execution bridge target

Status: **metadata/runtime-inspection surface VERIFIED; exact external enqueue implementation still requires one end-to-end proof**.

This is one of the most important engineering documents for implementing the semantic Lua/Game actions discovered elsewhere in the KB without destabilizing Unity.

## Verified class

Namespace/class:

`FGStudio.Engine.Utilities.MainThread`

Runtime metadata inspection on this frozen client has exposed these members:

### Static property

- `get_Instance()`
- `set_Instance(FGStudio.Engine.Utilities.MainThread)`.

### Unity lifecycle / dispatcher methods

- `Awake()`
- `Update()`
- `Execute(System.Action)`
- `StartCoroutine(System.Collections.IEnumerator)`
- `StopCoroutine(UnityEngine.Coroutine)`
- `DoExecuteWorks()`
- `.ctor()`.

### Fields observed

- `<Instance>k__BackingField`
- a `System.Collections.Concurrent.ConcurrentQueue<System.Action>` field whose metadata/string name is `waitToBeProcess`.

## Strong architectural interpretation

The combination:

- singleton `Instance`;
- `ConcurrentQueue<Action>`;
- `Execute(Action)`;
- Unity `Update()`;
- `DoExecuteWorks()`

strongly indicates a producer/consumer dispatcher where work can be queued from another thread and drained from the Unity-side update loop.

The existence of the fields/methods is VERIFIED. The exact control flow `Execute -> enqueue -> Update/DoExecuteWorks -> invoke` should be treated as **PROBABLE until direct method disassembly/runtime tracing is recorded in this KB**.

## Why this is preferable to direct arbitrary-thread invocation

Many actions now have exact semantic endpoints:

- `AutoFight_Main:StartAutoFight(Train)`
- `Game.GoTo`
- `Game.ClickNPC`
- `Game.RequestUsingSkillWithTarget`
- `Network.SendPacket`
- Lua UI callbacks.

The remaining stability risk is execution context. Calling Unity/Lua/gameplay methods from an arbitrary external worker thread can produce:

- Unity object access from the wrong thread;
- stale/lifecycle races;
- UI transition races;
- disconnect/crash/no-op behavior.

A game-owned MainThread dispatcher is therefore the preferred target for the Action Queue stage.

## Recommended architecture

```text
External process/controller
 -> Resolver
 -> read-only Scanner
 -> Snapshot/Observer
 -> State Machine
 -> Safety Guard
 -> Action Queue (max one mutable action)
 -> bridge creates/queues semantic action
 -> FGStudio.Engine.Utilities.MainThread.Execute(Action)
 -> game-owned main-thread execution
 -> observer waits for state proof
```

Do not issue the next mutable action until the first action's expected state transition is observed or a timeout/failure path is taken.

## Exact verification plan

Before declaring the dispatcher path fully VERIFIED:

1. resolve `MainThread.Instance` on a live client;
2. confirm it is non-null after normal scene/bootstrap initialization;
3. inspect/disassemble `Execute` and `DoExecuteWorks` or trace them read-only;
4. verify `Execute(Action)` causes the Action to be processed on the same Unity thread that runs `Update()`;
5. test one harmless semantic callback first;
6. record Unity thread ID and action execution thread ID;
7. only then use it for mutable gameplay/UI actions.

## Harmless proof candidates

Prefer a read-only/logging or non-destructive UI/state callback for first proof. Do not use selling, item deletion, revive or movement as the first dispatcher test.

## Lifetime rules

- resolve the singleton per game process;
- never reuse a MainThread instance pointer across different game processes;
- revalidate after process restart;
- do not assume a UI child object survives a panel close/reopen even if MainThread itself is stable;
- if a scene/bootstrap transition can recreate the dispatcher, revalidate instance identity.

## Relationship to `MonoBehaviourExecutor`

The Lua GUI path (`MainCallUI/CallUI`) uses `MonoBehaviourExecutor` for Lua script/UI lifecycle, while `FGStudio.Engine.Utilities.MainThread` appears to be a general Action dispatcher.

These are complementary layers:

- MainThread = where a cross-thread action should execute;
- Lua/Game/GUI API = what semantic action should execute.

## Important non-goal

`il2cpp_runtime_invoke` being exported does **not** prove a method is safe to call from an arbitrary thread. Runtime invocation mechanics and Unity thread affinity are separate concerns.

Use `runtime_invoke` only as an invocation primitive when the target execution context and object lifetime are already valid.

## Future AI rule

Do not redesign the tool around `CreateRemoteThread` or a continuously running remote worker for gameplay actions if the game-owned main-thread dispatcher can be proven and used. Preserve the architecture:

`Resolver -> Scanner -> Snapshot -> Observer -> State Machine -> Safety Guard -> Action Queue(1) -> MainThread Dispatcher -> Internal Action`.
