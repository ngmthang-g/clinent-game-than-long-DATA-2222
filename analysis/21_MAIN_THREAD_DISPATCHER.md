# FGStudio MainThread dispatcher — exact execution bridge

Status: **dispatcher internal control flow VERIFIED by metadata + direct GameAssembly disassembly. External bridge construction of a valid `System.Action` still requires one live end-to-end proof.**

This is a major engineering result. The game-owned dispatcher is no longer merely a candidate inferred from method names: its native implementation has been resolved and the full queue path has been observed.

## Exact class

Namespace/class:

`FGStudio.Engine.Utilities.MainThread`

Metadata TypeDefinition index:

- decimal `2931`
- hex `0xB73`.

Source-path strings present in the frozen binary/metadata include:

- `Assets\Scripts\Engine\Utilities\Threading\MainThread\MainThread.cs`
- `MainThread_API.cs`
- `MainThread_Core.cs`
- `MainThread_Define.cs`.

## Exact method table

Type methodStart = `24029`, method_count = `9`.

| Method | Metadata token RID | GameAssembly RVA | VA |
|---|---:|---:|---:|
| `get_Instance()` | `0x2AB7` | `0x601360` | `0x180601360` |
| `set_Instance(MainThread)` | `0x2AB8` | `0x6013A0` | `0x1806013A0` |
| `Awake()` | `0x2AB9` | `0x601130` | `0x180601130` |
| `Update()` | `0x2ABA` | `0x6012D0` | `0x1806012D0` |
| `Execute(System.Action)` | `0x2ABB` | `0x601250` | `0x180601250` |
| `StartCoroutine(IEnumerator)` | `0x2ABC` | `0x6012B0` | `0x1806012B0` |
| `StopCoroutine(Coroutine)` | `0x2ABD` | `0x6012C0` | `0x1806012C0` |
| `DoExecuteWorks()` | `0x2ABE` | `0x601190` | `0x180601190` |
| `.ctor()` | `0x2ABF` | `0x6012E0` | `0x1806012E0` |

These pointers were resolved through the `Assembly-CSharp.dll` IL2CPP CodeGenModule. Its methodPointerCount is `0x3190` = 12,688 and method-pointer table address is `0x1834BCD70` in this frozen image.

Historic RVAs are evidence/debug locators for this snapshot; future implementation should still prefer semantic metadata resolution over hardcoding them as the only identity.

## Fields

Verified fields:

- static `<Instance>k__BackingField`
- `System.Collections.Concurrent.ConcurrentQueue<System.Action> waitToBeProcess`.

Direct constructor disassembly shows the queue reference is stored at native instance offset:

`this + 0x20`.

## `.ctor()` — queue allocation VERIFIED

At RVA `0x6012E0`, the constructor allocates/initializes a `ConcurrentQueue<System.Action>` and stores it into the instance field around:

```text
lea rcx,[rdi+0x20]
mov [rdi+0x20],rbx
```

It then continues to the MonoBehaviour/base constructor path.

Conclusion:

**`waitToBeProcess` is an initialized per-instance concurrent Action queue at offset `0x20`.**

## `Awake()` — singleton setup VERIFIED

RVA `0x601130` writes the current `this` instance into static `<Instance>k__BackingField`.

Therefore normal Unity lifecycle establishes:

`MainThread.Instance = this`.

`get_Instance()` at RVA `0x601360` reads the static backing field; `set_Instance()` at `0x6013A0` writes it.

## `Execute(System.Action)` — enqueue semantics VERIFIED

Windows x64 instance-call register convention at entry:

- `RCX = this`
- `RDX = System.Action`.

At RVA `0x601250`, native code loads:

`[this + 0x20]`

and passes the queue plus supplied Action into the ConcurrentQueue enqueue implementation (resolved call/tail-jump around VA `0x180F7C390`). Null queue follows the generated throw path.

Observed key access:

```text
mov rcx,[rbx+0x20]
...
jmp/call 0x180F7C390
```

Conclusion:

**`MainThread.Execute(action)` enqueues `action` into `waitToBeProcess`.**

This is no longer PROBABLE.

## `Update()` — every-frame drain entry VERIFIED

RVA `0x6012D0` is effectively a thin wrapper:

```text
xor edx,edx
jmp 0x180601190   ; DoExecuteWorks
```

Conclusion:

**Unity `Update()` invokes `DoExecuteWorks()` each frame.**

## `DoExecuteWorks()` — dequeue + Action invoke loop VERIFIED

RVA `0x601190` performs the queue consumer loop.

Observed structure:

1. load queue from `[this+0x20]`;
2. check whether it is empty (call around VA `0x180F81A00`);
3. if empty, return;
4. otherwise call the ConcurrentQueue dequeue/TryDequeue path (around `0x180F7FE60`) with an out Action;
5. if returned Action is non-null, load delegate internals and invoke it via the delegate virtual invocation slot;
6. loop until the queue becomes empty.

The Action invocation region includes a call through:

```text
call QWORD PTR [rax+0x18]
```

after loading the delegate target/method data from the Action object.

Conclusion:

**`Update -> DoExecuteWorks -> TryDequeue -> invoke Action -> repeat until empty`.**

This is the exact game-owned main-thread producer/consumer path.

## End-to-end dispatcher truth

The frozen client therefore implements:

```text
producer thread/context
        |
        v
MainThread.Execute(System.Action)
        |
        v
ConcurrentQueue<Action>.Enqueue
        |
        |   (thread-safe queue boundary)
        v
Unity MainThread.Update()
        |
        v
DoExecuteWorks()
        |
        v
TryDequeue Action
        |
        v
Action.Invoke() on Unity Update thread
```

The static/native dispatcher behavior itself is **VERIFIED**.

## What remains unverified

The remaining problem is narrower: an external tool must prove it can safely construct/retain a valid managed `System.Action` and call `MainThread.Execute(action)` through the live IL2CPP bridge.

Still required once at runtime:

1. resolve `MainThread.Instance` per PID and confirm non-null;
2. create a valid managed `System.Action` whose delegate target/thunk remains alive long enough;
3. enqueue it through `Execute`;
4. make the first callback harmless/non-destructive;
5. record producer thread ID and callback thread ID to prove the callback executes on Unity Update thread;
6. verify no GC/lifetime corruption;
7. only then route gameplay/UI mutations through this path.

Do **not** claim this final external Action-construction step is solved merely because the internal queue is solved.

## Recommended architecture

```text
External Controller
 -> Resolver
 -> read-only Scanner
 -> Snapshot Store
 -> Observer
 -> State Machine
 -> Safety Guard
 -> Action Queue (max 1 mutable action)
 -> build/retain valid System.Action
 -> MainThread.Instance.Execute(Action)
 -> Unity Update drains queue
 -> semantic Lua/Game/UI action
 -> state proof
 -> next action
```

## Why this supersedes the legacy remote-worker design

Many gameplay semantics are already known:

- `StartAutoFight(C_AutoModel.Train)`
- `Game.GoTo`
- `Game.ClickNPC`
- `Game.RequestUsingSkillWithTarget`
- packet/Lua UI actions.

The old risk was invoking those on an arbitrary worker thread. The game already provides a concurrency boundary specifically shaped as `ConcurrentQueue<Action> -> Update -> Invoke`.

Therefore production mutable actions should target this dispatcher rather than a continuously running `CreateRemoteThread`/remote-worker gameplay executor.

## Lifetime/process rules

- resolve singleton separately for every game PID;
- never share MainThread/object/delegate pointers between clients;
- re-resolve after process restart;
- revalidate Instance after major bootstrap/scene lifecycle if needed;
- never retain child UI pointers across close/reopen transitions;
- keep at most one mutable external action pending until state proof/timeout resolves it.

## Relationship to `MonoBehaviourExecutor`

`MonoBehaviourExecutor` remains the Lua/UI script lifecycle layer used by `MainCallUI/CallUI`.

The roles are complementary:

- **MainThread dispatcher** = where externally-originated work should execute;
- **Lua/Game/GUI semantic APIs** = what work should execute.

## Important rule

`il2cpp_runtime_invoke` is an invocation primitive, not a thread-safety guarantee. If it is used to call `MainThread.Execute`, that can be appropriate because the supplied Action itself is deferred to Unity Update. Do not use arbitrary-thread `runtime_invoke` directly on Unity/Lua gameplay mutations merely because the export exists.

## Future AI rule

Do not spend time rediscovering whether `Execute` really enqueues or whether `Update` really drains the queue. That part is now VERIFIED by direct disassembly. Future work should focus only on the **external managed Action construction/lifetime + one harmless live proof**.
