# Research TODO — current automation-tool gaps only

Status: **static foundation closed for the frozen snapshot** after full tool-first + all-75 Config materialization and exact InputSync signature/lifecycle recovery.

Main goal: future AI should build the Thần Long automation tool from this KB and **not repeat reverse/extraction already solved**.

Read first:

- `AUTO_TOOL_SCOPE.md`
- `AI_ROUTER.md`
- `database/TOOL_DATA_INDEX.md`
- `AUTO_FEATURE_READINESS.md`
- `research/AUTO_RUNTIME_PROOF_QUEUE.md`.

## Closed foundation work — do not redo

DONE for the frozen client:

- Unity x64 / IL2CPP metadata architecture and snapshot hashes.
- LuaSystem / Game / GUI / Network semantic bridge discovery.
- Config/Interface transform decode and extraction.
- exact recovery of **75 Config XML tables**.
- specialized tool-first static databases for Monster/Boss, Items/Equips, Skills/Magic, Tasks, FuBen, Pets/Spirits and PC bindings.
- structurally-lossless fallback for **every Config table** under `database/config_full/`.
- map/NPC/AutoPath databases.
- runtime nearby-player/enemy/target/bag/buff/team/map schemas.
- Train, target/chase/skill/loot donor.
- Auto Buff/Nga My identities and guards.
- exact Sell request and inventory-update lifecycle.
- item Use/Abandon/Move/Split/Destroy semantics.
- Revive/Đầu thai semantics.
- dynamic GameDialog architecture.
- Team leave/join/invite/follow semantics.
- Trade/dồn đồ protocol/session and 9-slot capacity.
- FuBen scenario/action/Boss flow and control packets.
- PK/AutoPK/retaliation semantics.
- Pet/Spirit runtime donor.
- MainThread queue/Update/Action.Invoke static internals.
- per-PID runtime snapshot/action arbitration model.
- InputSync exact static contract for the frozen build: declaring types, signatures, metadata tokens, selected native RVAs, generated x64 ABI, screen conversion, ParseAndInject UI call graph and drag-state lifecycle.

### InputSync corrections now closed

Do not search the wrong class:

```text
TryClickUI / UpdateUIDrag / EndUIDrag / CancelUIDragState / ResetUIDragState
 -> InputSyncManager

SetSyncState / GetSyncGroupId / SetSyncGroup
 -> InstanceRegistry

FramePressState
 -> PointerEventData+FramePressState

GetLastPointerEventData
 -> PointerInputModule

Joystick.InjectSyncInput
 -> Joystick in Assembly-CSharp-firstpass
```

Canonical InputSync implementation evidence:

- `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
- `database/PC_INPUTSYNC_METHODS.csv`.

Do not broad-disassemble GameAssembly again for this same hidden-click contract unless hashes change or a genuinely new method is required.

## Static Config data is not a TODO

Canonical specialized manifest:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

Canonical all-table catalog:

`database/config_full/CONFIG_FULL_CATALOG.csv`

Canonical router:

`database/TOOL_DATA_INDEX.md`

Generators:

- `tools/materialize_tool_data.py`
- `tools/materialize_all_config.py`.

Workflow:

`.github/workflows/materialize-tool-data.yml`

If a future Config snapshot changes, regenerate/compare. Do not manually rediscover schemas.

---

# P0 — production integration proof

## External managed Action -> MainThread callback

Static dispatcher architecture is solved:

```text
MainThread.Execute(System.Action)
 -> ConcurrentQueue<Action>
 -> Unity Update
 -> DoExecuteWorks
 -> Action.Invoke
```

Remaining work is production integration only:

```text
external tool constructs + roots one valid Action
 -> enqueue through MainThread.Execute
 -> next Unity Update invokes callback
 -> observe a harmless known state transition
```

If this fails, debug delegate construction/rooting/lifetime/resolver/thread boundary. Do not reverse MainThread again.

Canonical docs:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`
- `contracts/MAINTHREAD_BRIDGE_V1.md`.

---

# P1 — runtime/server proofs

## Nga My beneficial-skill acceptance outside team

Already solved: nearby PeacePlayer state, skill IDs/properties/range/cooldown, select/chase/cast path.

Still server-authoritative: acceptance for the exact production skill on same team, same guild outside team, unrelated peaceful player and self where applicable.

Proof requires one real cast plus fresh HP/buff/cooldown/progress result.

## NPC Trị liệu dynamic dialog

Static NPC identity/navigation and GameDialog mechanism are solved.

Still live-dependent:

```text
current interaction
 -> current GameDialog.Selections
 -> exact visible service text
 -> current selectionID
 -> optional confirmation
 -> HP/money/dialog result
```

SelectionID is dynamic state, not a frozen global constant.

## Auto Sell vendor promotion

Static NPC candidates/navigation and exact sell request are solved.

For each production vendor:

```text
GoToNPC
 -> current service/dialog selection
 -> CMD_NPC_SHOP_DATA
 -> current NpcShopID + ShopID + IsGuildShop
 -> optional safe test sale
 -> bag/money proof
```

Do not hardcode observed shop/session IDs without stability evidence.

## FuBen production lifecycle

Static 19-scenario routes/actions/Boss joins are solved. Add live evidence only when a concrete scenario fails due to current server condition/dialog/matchmaking/completion behavior.

## Trade/dồn đồ production session proof

Protocol/session is solved. Live implementation proof remains:

```text
request MAIN RoleID
 -> active ExchangeID
 -> add fresh live instances
 -> verify ItemsTrade
 -> both locks
 -> Done
 -> session close
 -> fresh MAIN/CON bags
```

Elapsed time or click completion is not proof of item transfer.

---

# P2 — optional richer observations

Only investigate for a concrete feature need:

- arbitrary non-team PeacePlayer exact Position/death;
- absolute HP/MaxHP for every unselected monster;
- richer arbitrary-target BuffID/duration list;
- localization/Translations only when live text matching becomes ambiguous;
- `data.unity3d` scene/prefab details only when Maps/NPC/AutoPath/runtime path APIs cannot answer the specific problem.

Do not broad-extract these merely for completeness.

---

# Implementation work, not research

Normally solve in the actual tool source:

- state-machine bugs;
- stale snapshots/item instances;
- timeout/retry/arbitration;
- multi-PID scheduler/isolation;
- tool UI/settings;
- Telegram reporting;
- licensing/update/security;
- item keep/sell/drop policy;
- map/spot prioritization;
- InputSync per-machine bootstrap/PID/window/DPI validation using the now-known exact static contract.

## Evidence recording rule

Any new runtime proof should record:

```text
client snapshot/hash
feature
pre-state
exact IDs/action/payload
observed event/state sequence
final state
PASS / FAIL / PARTIAL
what it proves
what it does NOT prove
```

Then update the canonical feature doc, `AUTO_FEATURE_READINESS.md` and the runtime proof queue.

## Hard rule

**If `database/TOOL_DATA_INDEX.md`, `database/config_full`, the action/API catalogs and canonical analyses already answer the question, do not reverse/decrypt the client again.**
