# Static Config database — query-oriented storage

Status: **MATERIALIZED on `main` from the verified frozen `Config.unity3d` snapshot.**

The previous placeholder state is closed: full/compact normalized data now exists under `database/static/`, generated reproducibly by `tools/materialize_tool_data.py` and validated by GitHub Actions.

Canonical navigation: `database/TOOL_DATA_INDEX.md`.

## Current materialized domains

### Combat / skills

`skills/`

- Skills — **2,091** (`SKILL_TOOL_INDEX.csv`, `SKILL_INDEX.csv`, full `SKILLS_*` chunks)
- SkillProperties — **2,044** (`SKILL_PROPERTIES_*`)
- AutoSkills — **300** (`AUTO_SKILLS.csv`)
- MagicAtrributes — **509** in `../magic/MAGIC_ATTRIBUTES.csv`
- Factions — **17**
- Books — **128**
- BookLevelUpCost — 9 rows.

### Inventory / equipment

`items/`

- Items — **5,238** (`ITEM_TOOL_INDEX.csv`, `ITEM_INDEX.csv`, full `ITEMS_*` chunks)
- Medicines — **692**
- Gems — **1,154**
- `ITEM_POLICY_EXCEPTIONS.csv` for templates requiring extra keep/sell/drop caution.

`equips/`

- Equips — **22,763** in compact indexes + full chunks
- Weapon templates (`EquipPoint==0`) — **4,685** in `WEAPON_INDEX.csv`
- position/type summary in `EQUIP_POSITION_TYPE_COUNTS.csv`.

### World / combat targets

`monsters/`

- Monsters — **17,121** in `MONSTER_INDEX_*`
- exact `Type=Boss` templates — **3,579** in `BOSS_INDEX_*`
- distinct Boss names — **578** in `BOSS_NAME_INDEX.csv`.

Maps/NPC/AutoPath remain in the dedicated root database paths rather than being duplicated here.

### Tasks / activities

`tasks/`

- Tasks — **516** (`TASK_INDEX.csv`, full `TASKS_*` chunks)
- normalized task objective records — **591** (`TASK_OBJECTIVES.csv` + chunks)
- GrowPoints — **407**
- GuildTask — **360**
- Activities — **45**.

### Pet / Spirit

`pets/`

- Pets — **8,349** in compact indexes + full chunks
- Spirits — **1,889** in compact index + full chunks
- PetFeatures / PetEquips / PetEquipSets / SpiritFeatures are materialized alongside them.

## FuBen is separate by design

Dungeon/scenario data lives in `database/fuben/` because it joins route/action runtime semantics rather than being a generic static table dump.

Use:

- `FUBEN_SCENARIOS.csv`
- `FUBEN_ENTRY_NPCS.csv`
- `FUBEN_ACTIONS_COMPACT.csv`
- `FUBEN_KILL_TARGETS.csv`
- `FUBEN_BOSS_LEVEL_BANDS.csv`
- `actions/FUBEN_ACTIONS_*.csv`.

## Lookup strategy

Large static databases are lookup systems, not mandatory context.

```text
identify subsystem
 -> open database/TOOL_DATA_INDEX.md
 -> use smallest compact index
 -> open one relevant row/chunk
 -> use canonical analysis only for semantic meaning
 -> use fresh runtime state before any mutable action
```

Examples:

- Boss by name -> `monsters/BOSS_NAME_INDEX.csv` -> one `BOSS_INDEX_*` chunk.
- arbitrary MonsterID -> matching `MONSTER_INDEX_*` chunk.
- ItemID -> `items/ITEM_TOOL_INDEX.csv` or matching `ITEMS_*` chunk.
- EquipID -> matching `EQUIP_INDEX_*`; full `EQUIPS_*` only for deeper attributes.
- SkillID -> `skills/index/SKILL_TOOL_INDEX_*`; then properties only if needed.
- TaskID -> `tasks/TASK_INDEX.csv` -> `TASK_OBJECTIVES.csv` -> full task chunk only if needed.

## Lossless preservation rule

Generated full chunks preserve source fields and nested structures where relevant. Compact indexes intentionally expose only routing/tool fields.

Do not delete a full chunk merely because a current feature does not use every field. The compact index prevents overread; the full chunk prevents future re-decryption/reparsing.

## Static/runtime authority boundary

Static data describes templates/configuration.

Mutable actions still require current runtime/server state.

Inventory:

```text
static Item/Equip template
 -> fresh dbItemData.ID instance
 -> fresh Site/Position/Bound/current rules
 -> one action
 -> server/runtime proof
```

Skills:

```text
static skill target/range/property
 -> current role ownership/condition/cooldown
 -> current target/range
 -> cast
 -> runtime/server proof
```

Monsters/tasks/pets:

```text
static template/objective
 -> current spawned/current task/current companion state
 -> action
 -> fresh proof
```

## Weapon rule

`Equips.EquipPoint == 0` = Weapon position.

Do **not** use `Type < 10` as a universal weapon test.

## Reproducibility

Authoritative generator:

`tools/materialize_tool_data.py`

Workflow:

`.github/workflows/materialize-tool-data.yml`

Manifest of generated paths, row counts and byte sizes:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

When the frozen Config snapshot changes, regenerate through this pipeline instead of manually editing thousands of CSV rows.
