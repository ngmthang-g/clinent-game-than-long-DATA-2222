# Database navigation index

> Machine/AI-readable data derived from the frozen client's decrypted Config/Interface/Lua plus verified runtime/native evidence. Primary purpose: support the **Thần Long auto tool** so future AI does not broad-reverse solved client areas.

## Start here

For static/configured data lookup, the canonical router is now:

**`TOOL_DATA_INDEX.md`**

For implementation/runtime semantics:

- `AUTO_TOOL_API_CATALOG.md` — compact state/query API catalog.
- `AUTO_TOOL_ACTION_CATALOG.md` — exact semantic mutable actions, packet IDs/payloads and proof rules.
- `SUBSYSTEM_SOURCE_MAP.md` — subsystem -> runtime/Lua/static/action source.
- `SEMANTIC_JOIN_MAP.md` — how IDs and layers join.
- `FACTS.jsonl` — high-value exact facts/constants.
- `TOOL_DATA_MATERIALIZATION_MANIFEST.csv` — generated database paths, byte sizes and row counts.

General implementation route remains:

```text
AI_BOOTSTRAP.md
 -> AUTO_TOOL_SCOPE.md
 -> AI_ROUTER.md
 -> one feature/context pack
 -> TOOL_DATA_INDEX.md when static lookup is needed
```

## Static data is now materially present on `main`

The old state where `database/static/` contained only planning READMEs is closed.

The verified frozen Config snapshot is now materialized into query-oriented indexes/chunks, including:

- **17,121 Monsters**, including **3,579 exact Boss templates / 578 Boss names**;
- **22,763 Equips**, including **4,685 Weapon-position templates**;
- **5,238 Items**, **692 Medicines**, **1,154 Gems**;
- **2,091 Skills**, **2,044 SkillProperties**, **300 AutoSkills**, **509 MagicAttributes**;
- **516 Tasks**, **591 normalized objective records**, **407 GrowPoints**, **45 Activities**, **360 GuildTasks**;
- **8,349 Pets**, **1,889 Spirits**;
- full FuBen scenario/action/kill/entry/level-band datasets;
- 22 PC input key bindings.

Exact generated paths/counts: `TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

## World / map / NPC / route data

Already materialized outside `static/`:

- `MAPS.csv` — 193 maps.
- `npcs/NPCS_0001_0200.csv` ... `NPCS_1001_1003.csv` — all 1,003 NPC rows.
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv` — 506 NPC-mediated transitions.
- `AUTOPATH_PORTAL_EDGES.csv` — direct portal topology.
- `AUTOPATH_ITEM_DESTINATIONS.csv` — item/destination mappings.
- `NPC_SERVICE_CANDIDATES.md` — candidate service taxonomy; dynamic service proof remains runtime-authoritative.

Do not invent live NPC X/Y from static data when `Game.GetNPCPosition(npcID)` exists.

## FuBen / Boss

Use `fuben/`:

1. `FUBEN_SCENARIOS.csv`
2. `FUBEN_ENTRY_NPCS.csv`
3. `FUBEN_ACTIONS_COMPACT.csv`
4. `FUBEN_KILL_TARGETS.csv`
5. `FUBEN_BOSS_LEVEL_BANDS.csv`
6. `actions/FUBEN_ACTIONS_*.csv` for full rows.

Boss templates themselves live under `static/monsters/`.

NPC entry actor and combat Boss are different semantic classes.

Canonical semantics: `analysis/38_FUBEN_BOSS_TASK_TOOL_STACK.md`.

## Monsters / train targets / Bosses

Use `static/monsters/`:

- `MONSTER_INDEX_*` — all 17,121 templates.
- `BOSS_INDEX_*` — all 3,579 exact `Type=Boss` templates.
- `BOSS_NAME_INDEX.csv` — 578 grouped Boss names.

Static data classifies a target; current spawn/RoleID/Position/death remains runtime data.

## Items / equipment / use / sell / drop

Items: `static/items/`

- `ITEM_TOOL_INDEX.csv`
- `ITEM_INDEX.csv`
- full `ITEMS_*` chunks
- `ITEM_POLICY_EXCEPTIONS.csv`
- `MEDICINES.csv`
- `GEMS_*`.

Equipment: `static/equips/`

- `EQUIP_INDEX_*`
- full `EQUIPS_*`
- `WEAPON_INDEX.csv`
- `EQUIP_POSITION_TYPE_COUNTS.csv`.

Hard rule: static Weapon position = `EquipPoint==0`.

For any mutation, current `dbItemData.ID` instance is not the same thing as template `ItemID` or bag `Position`.

## Skills / Buff / Auto Train / PK

Use `static/skills/`:

- small `index/SKILL_TOOL_INDEX_*` chunks for normal lookup;
- `SKILL_TOOL_INDEX.csv` / `SKILL_INDEX.csv` for broad local search;
- full `SKILLS_*` rows;
- `SKILL_PROPERTIES_*`;
- `AUTO_SKILLS.csv`, `FACTIONS.csv`, `BOOKS.csv`.

Magic dictionary: `static/magic/MAGIC_ATTRIBUTES.csv`.

Runtime cooldown/ownership/target/acceptance remains authoritative.

## Tasks / quest / activities / gather

Use `static/tasks/`:

- `TASK_INDEX.csv`
- `TASK_OBJECTIVES.csv`
- full `TASKS_*`
- objective chunks
- `GROW_POINTS.csv`
- `ACTIVITIES.csv`
- `GUILD_TASKS.csv`.

Canonical runtime semantics: `analysis/23_TASK_QUEST_AUTOMATION.md`.

## Pets / Spirits

Use `static/pets/`:

- `PET_INDEX_*` / `PETS_*`
- `SPIRIT_INDEX_*` / `SPIRITS_*`
- feature/equipment support tables.

Canonical runtime semantics: `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`.

## Protocol / exact actions

Before reverse engineering a request, check:

- `AUTO_TOOL_ACTION_CATALOG.md`
- `PACKET_IDS.csv`
- `NETWORK_COMMAND_CATALOG.md`
- matching canonical feature analysis.

Packet name existence alone does not prove request payload semantics.

## PC input / hidden click

- `PC_INPUT_KEY_BINDINGS.csv` — shipped key mapping.
- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` — InputSync / TryClickUI / press-release-drag-state evidence.

Prefer semantic Game/UI action routes over physical key/mouse emulation.

## Data interpretation rules

1. Static Config describes **template/configured truth**.
2. Runtime/server state describes **current/live truth and action success**.
3. Item instance ID != ItemID != slot Position != Site.
4. NPCID -> static identity; current position/service/dialog remains runtime-authoritative.
5. Boss name alone is not enough: use exact Monster template/level-band when available.
6. Fixed delay is never success proof.
7. Response/event handler is not automatically a valid request action.
8. Large databases are lookup systems, not mandatory context.

## Regeneration / integrity

Generated database is reproducible directly from the frozen repo snapshot:

- generator: `../tools/materialize_tool_data.py`
- workflow: `../.github/workflows/materialize-tool-data.yml`
- source: `../Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`
- manifest: `TOOL_DATA_MATERIALIZATION_MANIFEST.csv`.

The GitHub workflow has successfully regenerated and committed the database. Future snapshot updates should modify the source snapshot/generator and regenerate instead of manually hand-editing thousands of rows.

## Remaining gaps are mostly runtime proofs

Static data presence should no longer be confused with server/runtime validation.

Use `research/AUTO_RUNTIME_PROOF_QUEUE.md` for unresolved live proofs such as dynamic healer/vendor dialogs, relationship-specific beneficial-skill acceptance, and production MainThread callback integration.
