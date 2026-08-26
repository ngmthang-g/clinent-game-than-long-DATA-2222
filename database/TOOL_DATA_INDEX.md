# Tool Data Index — canonical machine-readable lookup map

Status: **CURRENT for frozen client snapshot materialized on 2026-08-26.**

Purpose: future AI/tool work should resolve static identity from this database first and should **not decrypt/reverse the client again** for data already present here.

## Core rule

```text
feature/question
 -> smallest domain index below
 -> exact row/chunk only
 -> canonical analysis for semantics
 -> fresh runtime/server state for mutable actions
```

Static Config answers what a template/configured route **is**. Runtime/server state answers what currently exists, is spawned, is accepted, and whether an action succeeded.

## Materialization source and reproducibility

Authoritative source snapshot:

`Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Reproducible generator:

`tools/materialize_tool_data.py`

Automation workflow:

`.github/workflows/materialize-tool-data.yml`

Generation manifest:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

The pipeline performs:

```text
FG transform decode
 -> UnityFS extraction
 -> 75 Config XML TextAssets
 -> normalized/query-oriented CSV database
```

It was validated both locally and in GitHub Actions. Do not manually edit generated CSV rows unless fixing the generator/source interpretation.

---

## 1. Maps / NPC / travel / portals

Use:

- `MAPS.csv` — 193 maps.
- `npcs/NPCS_0001_0200.csv` ... `NPCS_1001_1003.csv` — all 1,003 NPC templates.
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv` — 506 NPC-mediated route edges.
- `AUTOPATH_PORTAL_EDGES.csv` — direct portal graph.
- `AUTOPATH_ITEM_DESTINATIONS.csv` — item-linked destinations.
- `NPC_SERVICE_CANDIDATES.md` — service candidate taxonomy; runtime proof still required for dynamic services.

Runtime movement authority remains `Game.GoTo`, `Game.GetNPCPosition`, current map readiness and current world objects.

---

## 2. FuBen / dungeon / Boss route

Directory: `database/fuben/`

Use in this order:

1. `FUBEN_SCENARIOS.csv` — 19 scenario definitions.
2. `FUBEN_ENTRY_NPCS.csv` — 19 gather/entry NPC mappings.
3. `FUBEN_ACTIONS_COMPACT.csv` — all 268 actions with common action fields.
4. `FUBEN_KILL_TARGETS.csv` — all 72 configured Kill actions with boss evidence.
5. `FUBEN_BOSS_LEVEL_BANDS.csv` — level-banded MonsterID resolution for FuBen targets.
6. `actions/FUBEN_ACTIONS_*.csv` — chunked full action rows including less-common/raw attributes.

Canonical semantics:

- `analysis/38_FUBEN_BOSS_TASK_TOOL_STACK.md`
- `features/AUTO_FUBEN.md`

Important: NPC entry/service actor != combat Boss. Boss identity is resolved through Monster templates and then current spawned runtime actor.

---

## 3. Monsters / Bosses / Auto Train target identity

Directory: `database/static/monsters/`

All frozen Monster rows are materialized:

- `MONSTER_INDEX_00001_02500.csv` ... `MONSTER_INDEX_15001_17121.csv` — **17,121** templates.
- `BOSS_INDEX_0001_1200.csv` ... `BOSS_INDEX_2401_3579.csv` — **3,579 exact `Type=Boss` templates**.
- `BOSS_NAME_INDEX.csv` — **578 distinct Boss display names** grouped for fast name lookup.

High-value fields include:

`ID, ResName, Name, Level, Type, MaxHP, Exp, attacks/defenses, MoveSpeed, Skills, AIID, Avarta, Scale`.

Use static Type/ID for classification; use runtime world state for current spawn, RoleID, Position, death and targetability.

---

## 4. Tasks / quests / gather / activities

Directory: `database/static/tasks/`

- `TASK_INDEX.csv` — all **516** task templates with offer/complete NPC/map joins.
- `TASKS_0001_0260.csv`, `TASKS_0261_0516.csv` — full task rows with preserved nested structures.
- `TASK_OBJECTIVES.csv` — **591 normalized objective records**.
- `objectives/TASK_OBJECTIVES_*.csv` — objective chunks.
- `GROW_POINTS.csv` — **407** gather/life-skill/quest target records.
- `GUILD_TASKS.csv` — **360** guild-task records.
- `ACTIVITIES.csv` — **45** activity records.

Canonical runtime logic:

`analysis/23_TASK_QUEST_AUTOMATION.md`

Do not OCR quest text when template + live `dbTaskData.Parameters` already supply structured semantics.

---

## 5. Items / bag / sell / use / drop / medicine / gems

Directory: `database/static/items/`

- `ITEM_TOOL_INDEX.csv` — all **5,238** Items with tool-relevant policy fields.
- `ITEM_INDEX.csv` — routing/classification index including ID family.
- `ITEMS_0001_1000.csv` ... `ITEMS_5001_5238.csv` — full Item chunks.
- `ITEM_POLICY_EXCEPTIONS.csv` — templates requiring extra caution because of sell/throw/bound/script semantics.
- `ITEM_TYPE_COUNTS.csv` — type distribution.
- `MEDICINES.csv` — all **692** medicines.
- `GEMS_0001_0600.csv`, `GEMS_0601_1154.csv` — all **1,154** gems.

Canonical mutable semantics:

- `analysis/04_INVENTORY_ITEMS_SHOP.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `analysis/41_BAG_ITEM_USE_DROP_POLICY_STACK.md`
- `features/AUTO_SELL.md`
- `features/BAG_ITEM_POLICY.md`

Never mutate by template ItemID alone. Live `dbItemData.ID` is the item instance used by Use/Abandon/Destroy/Move/Sell/Trade actions.

---

## 6. Equipment / weapon classification

Directory: `database/static/equips/`

All **22,763** equipment templates are materialized:

- `EQUIP_INDEX_00001_04000.csv` ... `EQUIP_INDEX_20001_22763.csv` — compact lookup.
- `EQUIPS_00001_02500.csv` ... `EQUIPS_22501_22763.csv` — deeper chunks with attributes/description.
- `WEAPON_INDEX.csv` — **4,685** templates with `EquipPoint == 0`.
- `EQUIP_POSITION_TYPE_COUNTS.csv` — slot/type distribution.

Hard rule:

`EquipPoint == 0` = Weapon position.

Do not use `Type < 10` as the universal weapon test.

---

## 7. Skills / combat / buff

Directory: `database/static/skills/`

- `SKILL_TOOL_INDEX.csv` — all **2,091** skills, compact tool fields.
- `index/SKILL_TOOL_INDEX_*.csv` — small search chunks.
- `SKILL_INDEX.csv` — expanded lookup.
- `SKILLS_0001_0700.csv` ... `SKILLS_1401_2091.csv` — full skill chunks.
- `SKILL_PROPERTIES_0001_0700.csv` ... `SKILL_PROPERTIES_1401_2044.csv` — all **2,044** SkillProperties.
- `AUTO_SKILLS.csv` — **300** automatic skill rules.
- `FACTIONS.csv` — **17** factions.
- `BOOKS.csv` — **128** books.
- `BOOK_LEVEL_UP_COST.csv` — related progression cost table.

Magic/effect dictionary:

`database/static/magic/MAGIC_ATTRIBUTES.csv` — **509** semantic effect symbols.

Canonical runtime semantics:

- `analysis/05_COMBAT_SKILLS_BUFFS.md`
- `analysis/17_BUFF_RUNTIME_SCHEMA.md`
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- `features/AUTO_BUFF.md`
- `features/AUTO_TRAIN.md`

Static range/target/property does not prove current ownership, cooldown or server acceptance.

---

## 8. Pets / Spirits

Directory: `database/static/pets/`

Pets:

- `PET_INDEX_*.csv` — all **8,349** Pet templates, compact lookup.
- `PETS_*.csv` — full chunks.
- `PET_FEATURES.csv`
- `PET_EQUIPS.csv`
- `PET_EQUIP_SETS.csv`

Spirits:

- `SPIRIT_INDEX_00001_01889.csv` — all **1,889** Spirit templates.
- `SPIRITS_00001_01000.csv`, `SPIRITS_01001_01889.csv`
- `SPIRIT_FEATURES.csv`

Canonical runtime semantics:

`analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`

---

## 9. PC input / hidden click support

- `PC_INPUT_KEY_BINDINGS.csv` — **22** shipped PC key bindings for SkillBar, joystick, QuickItemsBar and Tab target change.
- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` — InputSyncManager / TryClickUI / press-release-drag-state evidence.

Prefer semantic game/UI actions over keyboard-coordinate simulation. The key-binding table is a presentation/input mapping and fallback reference.

---

## 10. Exact actions / packets / runtime APIs

Use these before reverse engineering any request again:

- `AUTO_TOOL_API_CATALOG.md`
- `AUTO_TOOL_ACTION_CATALOG.md`
- `PACKET_IDS.csv`
- `NETWORK_COMMAND_CATALOG.md`
- `SUBSYSTEM_SOURCE_MAP.md`
- `SEMANTIC_JOIN_MAP.md`

Important solved domains include movement/target/skill, NPC/GameDialog, Sell, Use/Abandon/Move/Destroy, loot, Revive, Team, Trade and FuBen control.

---

## 11. What still cannot be frozen into a static database

These are **runtime/server proofs**, not missing reverse-engineered static data:

- external managed `System.Action` callback through `MainThread.Execute` from the production tool;
- server acceptance of specific Nga My beneficial skills on non-team relationships;
- current healer `GameDialog.Selections` IDs/text/confirmation and result;
- current vendor dialog -> `NpcShopID/ShopID` promotion for selected maps;
- optional richer arbitrary-target position/HP/buff state only when an implementation truly needs it.

See `research/AUTO_RUNTIME_PROOF_QUEUE.md`.

Do not call those “missing database rows”.

---

## 12. Anti-overread rule for future AI

Do not load every static row into context.

Examples:

```text
Boss name -> BOSS_NAME_INDEX -> one BOSS_INDEX chunk
MonsterID -> matching MONSTER_INDEX chunk
ItemID -> ITEM_TOOL_INDEX / one ITEMS chunk
EquipID -> matching EQUIP_INDEX chunk -> deeper EQUIPS chunk only if needed
SkillID -> small SKILL_TOOL_INDEX chunk -> SkillProperties only if needed
TaskID -> TASK_INDEX -> TASK_OBJECTIVES -> full TASKS chunk only if needed
FuBen -> FUBEN_SCENARIOS -> compact actions -> exact action/full chunk
```

The database is deliberately complete enough for lookup while remaining routeable. Future AI should reverse native/client code only when a genuinely new semantic contract is absent from both this data layer and canonical analysis.
