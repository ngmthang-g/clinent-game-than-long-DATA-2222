# Research TODO — current automation-tool gaps only

Status updated after the 2026-08-26 full tool-data materialization.

Main goal: future AI should build the **Thần Long automation tool** from the frozen knowledge base and **not repeat client reverse/extraction that is already solved**.

Read first:

- `AUTO_TOOL_SCOPE.md`
- `AI_ROUTER.md`
- `database/TOOL_DATA_INDEX.md`
- `research/AUTO_RUNTIME_PROOF_QUEUE.md`.

## Closed foundation work — do not redo

The following are DONE for the frozen client snapshot:

- Unity x64 / IL2CPP metadata architecture.
- LuaSystem / Game / GUI / Network semantic bridge discovery.
- Config/Interface custom transform decode and extraction.
- 75 Config XML table recovery.
- Lua/UI callback cataloging and major automation flow tracing.
- map/NPC/AutoPath databases.
- runtime nearby-player/enemy/target/bag/buff/team/map schemas.
- semantic Train start/stop, target/chase/skill/loot donor.
- Auto Buff/Nga My core identities and action guards.
- exact Sell request and server-driven inventory update lifecycle.
- exact item Use/Abandon/Move/Split/Destroy semantics where documented.
- Revive/Đầu thai packet/type semantics.
- dynamic GameDialog architecture.
- Team leave/join/invite/follow semantics.
- Trade/dồn đồ invitation/session/actions and 9-slot capacity semantics.
- FuBen scenario/action/Boss flow and control packet semantics.
- AutoPK modes/target flow/retaliation semantics.
- Pet/Spirit runtime donor.
- MainThread queue/Update/Action.Invoke static internals.
- InputSync/TryClickUI/press-release-drag-state static anchors.
- per-PID runtime snapshot/action arbitration architecture.

## Static Config data is now materialized — not a TODO

The previous P1 task to normalize Items/Equips/Skills/Monsters/Tasks/Pets/Spirits is CLOSED.

Canonical generated-data manifest:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

Canonical lookup router:

`database/TOOL_DATA_INDEX.md`

Materialized on `main` includes:

- Monsters **17,121**; Boss templates **3,579**; grouped Boss names **578**.
- Equips **22,763**; Weapon-position templates **4,685**.
- Items **5,238**; Medicines **692**; Gems **1,154**.
- Skills **2,091**; SkillProperties **2,044**; AutoSkills **300**; MagicAttributes **509**.
- Tasks **516**; normalized objective rows **591**; GrowPoints **407**; GuildTasks **360**; Activities **45**.
- Pets **8,349**; Spirits **1,889**.
- FuBen **19 scenarios / 268 actions / 72 Kill actions** plus level-banded target mapping.
- PC input bindings **22**.

Generator:

`tools/materialize_tool_data.py`

Workflow:

`.github/workflows/materialize-tool-data.yml`

If the frozen `Config.unity3d` changes, regenerate/compare through the pipeline. Do not manually rediscover schemas or rerun broad reverse work.

---

# P0 — one production integration proof

## External managed Action -> MainThread callback

Static dispatcher architecture is solved:

```text
MainThread.Execute(System.Action)
 -> ConcurrentQueue<Action>
 -> Unity Update
 -> DoExecuteWorks
 -> Action.Invoke
```

What remains is production-tool integration proof only:

```text
external tool constructs + roots one valid managed Action
 -> enqueue through MainThread.Execute
 -> next Unity Update invokes callback
 -> tool observes a harmless known state transition
```

This is not a reason to reverse MainThread again.

Debug only delegate construction/rooting/lifetime/resolver/thread-boundary if the proof fails.

Canonical docs:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`
- `contracts/MAINTHREAD_BRIDGE_V1.md`.

---

# P1 — runtime/server proofs for important features

## Nga My beneficial skill acceptance outside team

Already solved:

- nearby PeacePlayer RoleID/HP/MaxHP/name/faction/guild;
- skill IDs/static properties/range/cooldown semantics;
- select/chase/cast action path.

Still server-authoritative:

- acceptance for the exact production skill when target is same team;
- same guild but not team;
- unrelated peaceful player;
- self where applicable.

Proof requires one real cast and fresh HP/buff/cooldown/progress result.

Do not infer server acceptance solely from static TargetType.

## NPC Trị liệu dynamic dialog

Static NPC identity and GameDialog mechanism are solved.

Still live/server-dependent:

```text
current NPC interaction
 -> current GameDialog.Selections
 -> exact visible Trị liệu/service text
 -> current selectionID
 -> possible confirmation dialog
 -> HP/money/dialog result
```

SelectionID is dynamic session/dialog state, not a frozen global Config constant.

## Auto Sell vendor promotion for configured maps

Static NPC candidates, navigation and exact sell request are solved.

For each vendor actually used by production:

```text
GoToNPC
 -> current service/dialog selection
 -> CMD_NPC_SHOP_DATA
 -> fresh NpcShopID + ShopID + IsGuildShop
 -> optional one safe test sale
 -> RemoveItem/bag/money proof
```

Do not hardcode observed `NpcShopID/ShopID` as eternal constants without stability evidence.

## FuBen server acceptance / dynamic lifecycle

Static scenario/action/Boss data is now complete for the frozen Config and shipped Lua flow is traced.

Only capture additional live proof if a concrete scenario fails in production, for example:

- current matchmaking rejection reason;
- current dynamic GameDialog selection change;
- current server entry condition not represented in the frozen Config;
- current completion/reward transition.

Do not rediscover all 19 scenario routes because one server condition changed.

## Trade/dồn đồ production session proof

Protocol/session semantics are solved.

Only implementation/live proof remains when production tool uses the semantic path:

```text
request by MAIN RoleID
 -> active ExchangeID
 -> add current live instances
 -> verify ItemsTrade
 -> both locks
 -> Done
 -> session close
 -> fresh MAIN/CON bags
```

A completed click macro or elapsed time is not proof of successful transfer.

---

# P2 — optional richer runtime observations

Investigate only when a concrete policy truly needs them.

## Arbitrary non-team PeacePlayer Position/death

Current PeacePlayer list already provides identity/HP/MaxHP and target/chase APIs can often handle range/navigation.

Only map exact Position/death if the chosen Auto Buff policy cannot work reliably without it.

## Absolute HP/MaxHP for every unselected nearby monster

Basic Train/FuBen target selection does not require this because runtime target identity/death/Position and selected-target HP state are already sufficient.

Only prove it for a concrete boss-health/lowest-HP telemetry policy.

## Rich BuffID/duration for arbitrary targets

Local buffs are structured. Other-target buff proof may be handled by buff icons/cast cooldown/HP change.

Only pursue a richer arbitrary-target buff list if production recast suppression cannot be made reliable otherwise.

## Translations

`Translations.unity3d` has been decoded to valid UnityFS, but a full localization key/value DB is not currently necessary for normal tool work.

Extract/index it only if dynamic dialog/UI matching hits a real localization ambiguity that Config + Interface + live text cannot solve.

## data.unity3d / scene assets

Do not broad-extract the ~47 MB `data.unity3d` bundle.

Open it only for a concrete missing scene/path/prefab/resource question that cannot be answered by:

- `Game.GoTo` / runtime path APIs;
- Maps/NPC/AutoPath database;
- Config/Interface semantics.

---

# What is implementation work, not research

The following should normally be solved in the actual tool source rather than adding new reverse-engineering documents:

- state-machine bugs;
- stale snapshot/instance IDs;
- retry/timeout/arbitration policies;
- UI layout of the external tool;
- persistent settings;
- multi-PID scheduler behavior;
- Telegram reporting;
- licensing/update/security of the external tool;
- feature-specific production policy such as which items to keep or which map to prioritize.

Use the existing DATA to implement these; add new client facts only when the client/server contract itself was previously unknown.

---

# Evidence recording rule

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

Then update the canonical feature doc and `AUTO_FEATURE_READINESS.md` / `AUTO_RUNTIME_PROOF_QUEUE.md` as appropriate.

## Hard rule

**If `database/TOOL_DATA_INDEX.md`, the action/API catalogs, and the canonical feature analysis already answer the question, do not reverse/decrypt the client again.**
