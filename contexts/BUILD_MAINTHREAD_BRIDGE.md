# Context Pack — Build MainThread Bridge

## Scope

Use when implementing or debugging the external bridge that must execute semantic Game/Lua/UI work on Unity's main thread.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `contracts/MAINTHREAD_BRIDGE_V1.md` — build-ready implementation contract
3. `analysis/31_CURRENT_AUTO_TOOL_BRIDGE_INTEGRATION.md` — exact fit to current `AUTO-train-thanlong` source
4. `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md` — exact Action ABI/CTS proof details
5. `analysis/21_MAIN_THREAD_DISPATCHER.md` — queue consumer proof
6. `research/TODO.md`

`analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md` is supporting donor evidence; read it only if construction rationale needs re-checking. Read `analysis/01_IL2CPP_RUNTIME_METADATA.md` only when resolver/export details beyond the contract are actually needed.

## Current-tool shortcut

The current `AUTO-train-thanlong` bridge is **not** a foreign worker-thread design. Its `WH_GETMESSAGE` hook already proves, before read-only snapshot access:

```text
window TID == hook TID
il2cpp_thread_current() != null
SynchronizationContext.Current == UnitySynchronizationContext
CurrentThread.ManagedThreadId == Unity MainThreadId
```

Therefore the existing validated hook path is already a legitimate managed Unity-main-thread **producer context**. Do not call `thread_attach` again on that path.

Still enqueue mutations through `MainThread.Execute(Action)` so actual callback execution happens from the normal game-owned Update dispatcher rather than re-entrantly inside the Windows message hook.

## Critical async rule for this tool

Do **not**:

```text
hook -> Execute(Action) -> wait synchronously for Action result
```

The hook is on the Unity main thread; blocking it prevents the future Update that drains the Action.

Use the two-phase protocol from the contract:

```text
Begin proof -> construct/root/enqueue -> return from hook
[next Unity Update invokes Action]
Poll proof -> observe CTS state -> PASS/cleanup
```

Recommended new tool commands are `BeginMainThreadActionProof`, `PollMainThreadActionProof`, and `CleanupMainThreadActionProof`, with a protocol-version bump when shared structures change.

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

Generated `System.Action` constructor pattern:

```text
RCX = new Action object
RDX = managed target object, or null for static callback
R8  = callback MethodInfo*
R9  = null
```

Current frozen direct producer locators:

```text
System.Action ctor      GameAssembly + 0x49F810
MainThread.Execute      GameAssembly + 0x601250
```

A shipped caller enters Execute with:

```text
RCX = MainThread.Instance
RDX = Action
R8  = 0
```

Resolve semantic type/method identities first; treat RVAs only as this frozen snapshot's native implementation locators.

Do **not** forge delegate memory manually.

## Current bridge API delta

Existing `bridge.cpp` already resolves most read/query APIs. Add at minimum:

```text
il2cpp_object_new
il2cpp_gchandle_new
il2cpp_gchandle_get_target
il2cpp_gchandle_free
```

The current hook path already has `runtime_invoke`, corlib/class/method lookup, return-type inspection, `thread_current`, object unbox and field/type helpers.

## Canonical first live proof

Use:

```text
System.Threading.CancellationTokenSource
```

Exact frozen metadata cross-checks:

```text
zero-arg .ctor             token 0x0600120A
zero-arg Cancel()          token 0x0600120B
get_IsCancellationRequested token 0x06001203
```

Expected proof:

```text
false
 -> legitimate Action(target=CTS, callback=Cancel)
 -> MainThread.Execute(Action)
 -> return from hook
 -> Unity Update drains Action
 -> later Poll sees true
```

This proof does not move the player, touch UI, send packets, mutate items or alter social state.

## GC/lifetime rule

Use strong GC handles during the proof.

- root CTS through later Poll;
- root Action through enqueue; keeping it until PASS is fine for first proof;
- retrieve target from GC handle during Poll rather than trusting a cached raw pointer;
- cleanup must be idempotent and fail closed.

## Do not regress to

- direct gameplay mutations inside the WH_GETMESSAGE hook;
- direct arbitrary-worker-thread `Game.GoTo`, `UseSkill`, `ClickNPC`, Lua UI calls;
- production CreateRemoteThread gameplay worker;
- fake delegate memory layouts;
- synchronous waiting for an enqueued Action on Unity main thread;
- Sell/Abandon/Revive/party mutation as first bridge proof.

## Completion criteria

Promote external Action dispatch to VERIFIED only after:

1. existing Unity-main-thread proof passes;
2. CTS + Action are legitimately allocated/rooted;
3. Begin command enqueues and returns immediately;
4. a later Poll observes `IsCancellationRequested: false -> true`;
5. repeated tests show no exception/crash/GC corruption;
6. roots clean up safely.

Then test one low-risk semantic game action before migrating feature mutations.