# Tool Data Index — canonical machine-readable lookup map

Status: **CURRENT / CLOSED STATIC FOUNDATION for the frozen client snapshot.**

Purpose: future AI/tool work must resolve frozen static identity from this repository before considering any new reverse/decrypt work.

## Core lookup rule

```text
feature/question
 -> specialized tool-first index below
 -> exact row/chunk only
 -> canonical feature analysis for semantics
 -> database/config_full only if a specialized layer lacks the field/table
 -> fresh runtime/server state for mutable/current truth
```

Do not load large domains wholesale into context.

## Reproducibility

Authoritative source:

`Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Specialized generator:

`tools/materialize_tool_data.py`

All-75-table fallback generator:

`tools/materialize_all_config.py`

Workflow:

`.github/workflows/materialize-tool-data.yml`

Manifests/catalogs:

- `TOOL_DATA_MATERIALIZATION_MANIFEST.csv`
- `config_full/CONFIG_FULL_CATALOG.csv`
- `config_full/CONFIG_FULL_MANIFEST.csv`.

The all-Config workflow fails closed unless exactly **75 Config XML tables** are recovered.

---

## Maps / NPC / travel / portals

Use:

- `MAPS.csv` — 193 maps.
- `npcs/NPCS_*.csv` — all 1,003 NPC templates.
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv` — NPC-mediated routes.
- `AUTOPATH_PORTAL_EDGES.csv`
- `AUTOPATH_ITEM_DESTINATIONS.csv`
- `NPC_SERVICE_CANDIDATES.md`.

Runtime movement/service authority remains current `Game.GoTo`, `Game.GetNPCPosition`, live map objects, GameDialog and shop state.

## FuBen / dungeon / Boss

Directory: `fuben/`

Lookup order:

1. `FUBEN_SCENARIOS.csv` — 19 scenarios.
2. `FUBEN_ENTRY_NPCS.csv` — entry/gather NPCs.
3. `FUBEN_ACTIONS_COMPACT.csv` — all 268 actions.
4. `FUBEN_KILL_TARGETS.csv` — 72 Kill actions.
5. `FUBEN_BOSS_LEVEL_BANDS.csv` — level-banded MonsterID resolution.
6. `actions/FUBEN_ACTIONS_*.csv` — deeper action rows.

Canonical semantics:

- `analysis/38_FUBEN_BOSS_TASK_TOOL_STACK.md`
- `features/AUTO_FUBEN.md`.

NPC entry actor != combat Boss.

## Monsters / Bosses / Train targeting

Directory: `static/monsters/`

- `MONSTER_INDEX_*.csv` — **17,121** Monster templates.
- `BOSS_INDEX_*.csv` — **3,579 exact Type=Boss templates**.
- `BOSS_NAME_INDEX.csv` — **578 distinct Boss display names**.

Static template ID/type/name/AI/level is frozen truth. Current spawn/RoleID/position/death is runtime truth.

## Tasks / quest / gather / activities

Directory: `static/tasks/`

- `TASK_INDEX.csv` — **516** tasks.
- `TASKS_*.csv` — full task chunks.
- `TASK_OBJECTIVES.csv` — **591** normalized objectives.
- `objectives/TASK_OBJECTIVES_*.csv`
- `GROW_POINTS.csv` — **407**.
- `GUILD_TASKS.csv` — **360**.
- `ACTIVITIES.csv` — **45**.

Canonical runtime semantics: `analysis/23_TASK_QUEST_AUTOMATION.md`.

## Items / bag / sell / use / drop / medicine / gems

Directory: `static/items/`

- `ITEM_TOOL_INDEX.csv` — all **5,238** Items.
- `ITEM_INDEX.csv`
- `ITEMS_*.csv`
- `ITEM_POLICY_EXCEPTIONS.csv`
- `ITEM_TYPE_COUNTS.csv`
- `MEDICINES.csv` — **692**.
- `GEMS_*.csv` — **1,154**.

Canonical mutation semantics:

- `analysis/04_INVENTORY_ITEMS_SHOP.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `analysis/41_BAG_ITEM_USE_DROP_POLICY_STACK.md`
- `features/AUTO_SELL.md`
- `features/BAG_ITEM_POLICY.md`.

Never mutate by template ItemID alone. Use fresh live item instance ID.

## Equipment / weapons

Directory: `static/equips/`

- `EQUIP_INDEX_*.csv`
- `EQUIPS_*.csv` — all **22,763** equipment templates.
- `WEAPON_INDEX.csv` — **4,685** templates where `EquipPoint==0`.
- `EQUIP_POSITION_TYPE_COUNTS.csv`.

Hard rule: `EquipPoint == 0` is Weapon position. `Type < 10` is not a universal weapon test.

## Skills / combat / buff

Directory: `static/skills/`

- `SKILL_TOOL_INDEX.csv` — all **2,091** skills.
- `index/SKILL_TOOL_INDEX_*.csv`
- `SKILL_INDEX.csv`
- `SKILLS_*.csv`
- `SKILL_PROPERTIES_*.csv` — **2,044**.
- `AUTO_SKILLS.csv` — **300**.
- `FACTIONS.csv` — **17**.
- `BOOKS.csv` — **128**.
- `BOOK_LEVEL_UP_COST.csv`.

Magic/effect dictionary:

`static/magic/MAGIC_ATTRIBUTES.csv` — **509** rows.

Runtime ownership/cooldown/target legality/server acceptance remains authoritative.

## Pets / Spirits

Directory: `static/pets/`

- `PET_INDEX_*.csv`, `PETS_*.csv` — **8,349** Pets.
- `PET_FEATURES.csv`
- `PET_EQUIPS.csv`
- `PET_EQUIP_SETS.csv`
- `SPIRIT_INDEX_*.csv`, `SPIRITS_*.csv` — **1,889** Spirits.
- `SPIRIT_FEATURES.csv`.

Runtime semantics: `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`.

## Full fallback for every Config domain

Directory: `config_full/`

Use only when the specialized tool-first layer lacks a table or field.

Entry points:

- `config_full/README.md`
- `config_full/CONFIG_FULL_CATALOG.csv` — **all 75 recovered Config tables**.
- `config_full/CONFIG_FULL_MANIFEST.csv`.

Each table is stored under:

```text
config_full/<Table>/ROWS_*.csv
```

Rows preserve original direct XML attributes plus recursive nested child structure. Therefore low-frequency domains such as titles, reputation, guild configuration, mount/progression, cosmetics and other Config tables no longer require a new Config decrypt/extract pass.

## PC input / InputSync / hidden click

Presentation mappings:

- `PC_INPUT_KEY_BINDINGS.csv` — 22 key bindings.

Exact hidden-click method lookup:

- `PC_INPUTSYNC_METHODS.csv`
- `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` for discovery/background.

Important corrected ownership:

- `TryClickUI/UpdateUIDrag/EndUIDrag/CancelUIDragState/ResetUIDragState` -> `InputSyncManager`.
- `SetSyncState/GetSyncGroupId/SetSyncGroup` -> `InstanceRegistry`.
- `FramePressState` -> `PointerEventData+FramePressState`.
- `GetLastPointerEventData` -> `PointerInputModule`.
- `Joystick.InjectSyncInput` -> `Joystick` in Assembly-CSharp-firstpass.

Do not resolve those methods against the wrong declaring class.

For the exact frozen binary, core InputSync signatures, metadata tokens, selected native RVAs, native argument ABI, coordinate conversion and persistent drag-state lifecycle are now statically solved. Runtime per-PID object/bootstrap/window validation still belongs to the production tool.

## Exact actions / packets / runtime APIs

Use before tracing a request again:

- `AUTO_TOOL_API_CATALOG.md`
- `AUTO_TOOL_ACTION_CATALOG.md`
- `PACKET_IDS.csv`
- `NETWORK_COMMAND_CATALOG.md`
- `SUBSYSTEM_SOURCE_MAP.md`
- `SEMANTIC_JOIN_MAP.md`.

Solved domains include movement/target/skill, NPC/GameDialog, Sell, Use/Abandon/Move/Split/Destroy, loot, Revive, Team, Trade and FuBen control.

## Static vs runtime boundary

Static database answers what a configured/template object **is**.

Runtime/server state answers what currently exists/is accepted/succeeded, including:

- spawned actor state;
- current item instances and bag slots;
- current task progress;
- GameDialog selection IDs;
- shop/session IDs;
- team/trade/dungeon acceptance and completion;
- current cooldown/buff/HP state.

Remaining runtime proofs are tracked in `research/AUTO_RUNTIME_PROOF_QUEUE.md` and `research/TODO.md`.

## Anti-overread examples

```text
Boss name -> BOSS_NAME_INDEX -> one Boss/Monster chunk
MonsterID -> matching MONSTER_INDEX chunk
ItemID -> ITEM_TOOL_INDEX -> one ITEMS chunk only if needed
EquipID -> matching EQUIP_INDEX -> deeper EQUIPS chunk only if needed
SkillID -> SKILL_TOOL_INDEX chunk -> SkillProperties only if needed
TaskID -> TASK_INDEX -> TASK_OBJECTIVES -> full task chunk only if needed
FuBen -> scenario -> compact actions -> exact action/full chunk
Unknown Config table -> CONFIG_FULL_CATALOG -> one table chunk
Hidden click -> PC_INPUTSYNC_METHODS -> analysis/43
```

## Hard rule

**The frozen static foundation is closed. Search this repository before reversing/decrypting the client. Only reopen native/client analysis when the required semantic contract is genuinely absent or the client hashes change.**
