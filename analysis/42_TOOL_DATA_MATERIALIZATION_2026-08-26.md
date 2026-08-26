# 42 — Tool-first + all-Config materialization

Status: **MATERIALIZED AND VERIFIED ON `main`.**

This document supersedes every intermediate state where generated CSV paths existed only locally or only in analysis text.

## Source and reproducibility

Authoritative frozen source:

`Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Generators:

- `tools/materialize_tool_data.py` — specialized tool-first indexes/chunks.
- `tools/materialize_all_config.py` — structurally-lossless fallback for every Config table.

Workflow:

`.github/workflows/materialize-tool-data.yml`

The first specialized materialization was committed by GitHub Actions as:

`31a34a967d329284e05b40c0d47c7d98f721e05c` — `data: regenerate tool-first static database`.

The later all-table run succeeded and committed:

`51b795afc5117304fedf6b1ee15a75ea77855bc8` — `data: regenerate tool and all-Config databases`.

Canonical lookup:

`database/TOOL_DATA_INDEX.md`

Specialized manifest:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

All-table catalog/manifest:

- `database/config_full/CONFIG_FULL_CATALOG.csv`
- `database/config_full/CONFIG_FULL_MANIFEST.csv`.

## Specialized tool-first data now on main

### FuBen / Boss

- 19 scenarios
- 19 entry/gather NPC mappings
- 268 actions
- 72 Kill actions
- 1,381 FuBen level-band target mappings
- 17,121 Monster templates
- 3,579 exact `Type=Boss` templates
- 578 grouped Boss display names.

### Tasks / activities

- 516 Tasks
- 591 normalized objectives
- 407 GrowPoints
- 360 GuildTasks
- 45 Activities.

### Items / equipment

- 5,238 Items
- 692 Medicines
- 1,154 Gems
- 22,763 Equips
- 4,685 `EquipPoint==0` Weapon-position templates.

### Skills / combat support

- 2,091 Skills
- 2,044 SkillProperties
- 300 AutoSkills
- 509 MagicAttributes
- 17 Factions
- 128 Books.

### Pet / Spirit

- 8,349 Pets
- 1,889 Spirits
- associated Pet/Spirit feature/equipment tables.

### PC input

- 22 PC input key-binding rows.

## All 75 Config tables are now preserved

`tools/materialize_all_config.py` requires exactly **75** recovered Config XML TextAssets and writes:

```text
database/config_full/<Table>/ROWS_*.csv
```

Each top-level row preserves:

- original XML direct attributes using original names;
- row tag/index;
- recursive nested child tags/attributes/text in `ChildrenJSON`;
- root/table metadata in `CONFIG_FULL_CATALOG.csv`.

The current frozen catalog reports zero non-whitespace XML text nodes outside the attribute/child representation.

This closes the long-tail gap: guild/title/reputation/mount/progression/cosmetic and any other low-frequency Config domain no longer requires a new decrypt/extract pass merely to read frozen fields.

## Why both layers exist

Preferred route:

```text
specialized tool index -> exact specialized chunk
```

Fallback only when needed:

```text
CONFIG_FULL_CATALOG -> one config_full table chunk
```

The full fallback is not mandatory AI context.

## Evidence boundaries

- Static Config/database = frozen template/configured truth.
- Shipped Lua = client flow/action-construction truth.
- Native metadata/disassembly = executable static contract.
- Current runtime/server state = current spawn/instance/dialog/session/acceptance/completion truth.

Therefore static extraction is now closed for this snapshot. Remaining gaps in `research/AUTO_RUNTIME_PROOF_QUEUE.md` are live/server/integration proofs, not missing Config tables.
