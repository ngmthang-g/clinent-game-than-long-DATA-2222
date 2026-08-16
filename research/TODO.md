# Research TODO — targeted follow-up after deep static/Lua/native analysis

> General repository survey, asset decrypt, Config/Interface/Lua extraction, core packet/action discovery, MainThread dispatcher internals, Action constructor ABI and the AI routing layer are DONE. **Không broad reverse lại client từ đầu.**

## DONE — AI-native knowledge routing

- [x] `AI_BOOTSTRAP.md` compact mandatory entrypoint.
- [x] `AI_ROUTER.md` task-to-context routing.
- [x] task-specific `contexts/BUILD_*.md` packs for core/scanner/MainThread/Train/Buff/Sell/Heal/Revive/Party/Orchestrator.
- [x] `database/FACTS.jsonl` atomic high-value facts index.
- [x] `database/FACTS_README.md` usage/maintenance rules.
- [x] `database/FINDING_TO_DOC_MAP.md` linked to routing/context layer.
- [x] root README and `AI_INDEX.md` instruct AI not to preload the whole repository.

Normal future build path:

`AI_BOOTSTRAP -> AI_ROUTER -> one context pack -> REQUIRED docs -> specific database lookup`.

## DONE — architecture + semantic discovery

- [x] Unity x64 + IL2CPP architecture and metadata v39.
- [x] LuaSystemManager / SharedData / Game / GUI / Network bridges.
- [x] world/path/inventory/skill/buff symbol map.
- [x] `ClickNPC` internal flow.
- [x] `UIButton.HandleClickEvent` instance/stale-pointer hazard.
- [x] FG custom asset transform/decrypt.
- [x] 75 Config XML tables.
- [x] 338 UI layout XML files + 1,469 handler bindings.
- [x] readable Lua source and 339-class catalog.
- [x] 169 TCP packet constants.
- [x] 1,003 NPC + 193 map database.
- [x] 165 portal + 23 item destination + 506 NPC-mediated AutoPath edges.
- [x] 19 FuBen scenarios.
- [x] exact shop sell payload, revive values, bag sort/item action payloads.
- [x] dynamic `GameDialog.Selections` mechanism.
- [x] exact built-in Train start/state architecture.
- [x] nearby peaceful-player structured schema.
- [x] skill cooldown/QuickSkill semantics.
- [x] local buff duration/stack schema.
- [x] bag/shop event lifecycle.
- [x] team/follow runtime schema.
- [x] storage item-move/bank semantics.
- [x] loot/item-pack semantic engine.
- [x] task/quest and pet/spirit donor subsystems.

## DONE — MainThread dispatcher + producer ABI

Direct frozen-snapshot GameAssembly disassembly proves:

- [x] `MainThread.Awake()` establishes singleton Instance.
- [x] constructor creates `ConcurrentQueue<System.Action>` at `this+0x20`.
- [x] `Execute(Action)` enqueues into that queue.
- [x] `Update()` calls `DoExecuteWorks()`.
- [x] `DoExecuteWorks()` loops queue state -> dequeue -> Action invoke until empty.
- [x] shipped TCPGame/TCPLogin producers allocate legitimate managed targets/closures and Action delegates before calling Execute.
- [x] generated `System.Action` constructor call ABI is recovered: `RCX=Action`, `RDX=target or null`, `R8=callback MethodInfo*`, `R9=null` in observed calls.
- [x] same Action constructor is used with `RDX=0` in shipped static-callback call sites.
- [x] required semantic IL2CPP exports for class/method/type resolution, object allocation, runtime invoke, thread attach and GC handles are present.

Canonical evidence:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

Do **not** waste time reproving these static/native facts.

## P0 — External MainThread bridge: one live proof remains

The remaining execution-context problem is now extremely narrow: construct/root one valid managed Action from the external bridge, enqueue it and observe its callback result.

Canonical first proof:

```text
System.Threading.CancellationTokenSource
IsCancellationRequested=false
 -> Action target = CTS, callback = Cancel()
 -> MainThread.Execute(Action)
 -> Unity Update drains/invokes Action
 -> IsCancellationRequested=true
```

Required steps:

- [ ] Resolve live `MainThread.Instance` per game PID and confirm non-null.
- [ ] Attach producer context with `il2cpp_thread_attach(domain)` if it is not already an IL2CPP-attached thread.
- [ ] Resolve/allocate/initialize `System.Threading.CancellationTokenSource`.
- [ ] Strong-root CTS with `il2cpp_gchandle_new`.
- [ ] Resolve exact `Cancel()` overload and verify zero parameters + `System.Void` return.
- [ ] Resolve/allocate `System.Action`.
- [ ] Construct Action legitimately using target CTS + callback MethodInfo; do not forge fields.
- [ ] Strong-root Action during the first proof.
- [ ] Verify initial `IsCancellationRequested == false`.
- [ ] Enqueue through `MainThread.Execute(Action)`.
- [ ] Observe `IsCancellationRequested == true` within timeout.
- [ ] Confirm no managed exception/crash/GC corruption.
- [ ] Release roots after safe completion/cleanup.
- [ ] Repeat enough times to establish stability.
- [ ] Only after this proof route low-risk semantic Game/Lua/UI actions through the dispatcher.

Direct TID logging is optional diagnostic evidence. The primary proof combines the live CTS state transition with already-VERIFIED static `Update -> DoExecuteWorks -> Action.Invoke` semantics.

Do not replace this with a production `CreateRemoteThread` gameplay worker.

## P0 — NPC Trị liệu: targeted runtime proof only

- [ ] Open intended healer NPC (Lâu Lan candidate NPC `339` = Đỗ Thanh Đằng is static VERIFIED).
- [ ] Capture actual server-supplied `GameDialogData.Selections`.
- [ ] Identify visible Trị liệu/heal text and actual selectionID.
- [ ] Submit actual `selectionID:-1` through semantic GameDialog path.
- [ ] Record any second confirmation/dialog.
- [ ] Prove completion from HP/money/dialog state.
- [ ] Never assume a global fixed treatment selection ID unless repeated runtime evidence proves it.

## P0 — Runtime entity schema only where feature needs it

Structured UI paths already expose many useful fields. Only expand exact object layouts when needed by implementation:

- [ ] live bridge invocation of `GetNearByPeacePlayers` and copy returned fields into external snapshots.
- [ ] exact live Position/death/target fields needed for non-team support.
- [ ] exact NPC/Monster/Pet/ItemPack object fields only if current semantic APIs are insufficient.
- [ ] structured target-buff IDs/durations only if a future feature needs more than target buff icons.

## P1 — Machine-readable static database completion

Normalized schemas/counts are documented in `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`.

The large CSV chunks have been generated offline; repository upload remains to be completed:

- [ ] upload Items 5,238 rows.
- [ ] upload Skills 2,091 rows.
- [ ] upload MagicAtrributes 509 rows.
- [ ] upload Monsters 17,121 rows.
- [ ] upload Equips 22,763 rows.

Important static rule already documented: `EquipPoint=0` is Weapon; do not classify weapons only by subtype `Type`.

## P1 — Auto Sell / Store live validation

- [ ] use `GetFreeBagSpace` as source of truth.
- [ ] define explicit keep/sell/store policy.
- [ ] one current live instance -> one mutation -> wait item/shop/storage event -> rescan.
- [ ] verify NPCShop/storage service state before request.
- [ ] return to saved Train state only after map/position readiness proof.

## P1 — NPC service promotion

- [x] static service candidates exist.
- [ ] promote individual NPC -> service contracts only after dialog/shop/runtime evidence.

## P2 — Optional route planner

- [ ] use static portal + NPC-mediated edges for offline adjacency diagnostics if needed.
- [ ] keep runtime `Game.GoTo` as preferred executor.
- [ ] model level/event/state restrictions separately.

## Architecture guardrails

`Resolver -> read-only Scanner -> Snapshot/State Store -> Observer -> State Machine -> Safety Guard -> Action Queue (max 1 mutable action) -> valid System.Action -> MainThread.Execute(Action) -> Internal Action -> State Proof`

Rules:
- response handlers are not requests;
- stale UI pointers are not contracts;
- fixed delays are timeouts, never state proof;
- prefer semantic names/IDs over RVA;
- `ID` instance != `ItemID` template != `Position` slot != `Site` container;
- no invented NPC coordinates when `GetNPCPosition` exists;
- no invented treatment selection ID;
- no Captcha solving/bypass; pause for user verification.