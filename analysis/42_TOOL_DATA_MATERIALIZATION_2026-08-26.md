# 42 — Tool-first data materialization 2026-08-26

Status: **MATERIALIZED AND VERIFIED ON `main`.**

This document supersedes the earlier intermediate state where several CSVs had been generated locally but were not yet present in the repository tree.

## Source and reproducibility

Authoritative frozen source:

`Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`

Verified pipeline:

`tools/materialize_tool_data.py`

Automated regeneration:

`.github/workflows/materialize-tool-data.yml`

The pipeline was first tested locally against the supplied frozen client, recovering **75 Config XML tables**, then executed successfully by GitHub Actions. The successful workflow committed the generated database to `main` as:

`31a34a967d329284e05b40c0d47c7d98f721e05c` — `data: regenerate tool-first static database`.

Canonical machine-readable generated-file audit:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

Canonical lookup/navigation:

`database/TOOL_DATA_INDEX.md`

## Materialized FuBen / Boss data

`database/fuben/` now contains:

- `FUBEN_SCENARIOS.csv` — **19** scenarios.
- `FUBEN_ENTRY_NPCS.csv` — **19** entry/gather NPC mappings.
- `FUBEN_ACTIONS.csv` — **268** full normalized actions.
- `FUBEN_ACTIONS_COMPACT.csv` — compact view of the same **268** actions.
- `FUBEN_KILL_TARGETS.csv` — **72** Kill actions with configured monster/boss evidence.
- `FUBEN_BOSS_LEVEL_BANDS.csv` — **1,381** level-banded FuBen monster-template mappings.
- `actions/FUBEN_ACTIONS_*.csv` — full action chunks.

Boss lookup under `database/static/monsters/`:

- **17,121** Monster templates total.
- **3,579** exact `Type=Boss` templates.
- **578** grouped Boss display names in `BOSS_NAME_INDEX.csv`.

This closes the previous mismatch where the analysis referred to FuBen database paths that were not yet reachable on `main`.

## Materialized Tasks / activities

`database/static/tasks/` now contains:

- `TASK_INDEX.csv` — **516** task templates.
- full `TASKS_*` chunks — all 516 rows with preserved nested data.
- `TASK_OBJECTIVES.csv` — **591** normalized objective records.
- objective chunks — all 591 objective records.
- `GROW_POINTS.csv` — **407** records.
- `GUILD_TASKS.csv` — **360** records.
- `ACTIVITIES.csv` — **45** records.

Runtime task progress remains server-authoritative through current task state/Parameters.

## Materialized inventory / equipment data

Items under `database/static/items/`:

- **5,238** Item rows, compact indexes and full chunks.
- `ITEM_POLICY_EXCEPTIONS.csv` — high-caution templates for keep/sell/drop/use policy.
- **692** Medicines.
- **1,154** Gems.

Equipment under `database/static/equips/`:

- **22,763** Equip templates in indexes and full chunks.
- `WEAPON_INDEX.csv` — **4,685** `EquipPoint==0` Weapon-position templates.
- position/type counts.

This provides offline template policy data for Sell/Loot/Use/Drop/Trade, while current live item instance state remains required before mutation.

## Materialized Skills / combat-support data

`database/static/skills/` now contains:

- **2,091** Skills in tool index, expanded index and full chunks.
- **2,044** SkillProperties.
- **300** AutoSkills.
- **17** Factions.
- **128** Books.
- Book level-up cost table.

`database/static/magic/MAGIC_ATTRIBUTES.csv` contains all **509** magic/effect symbols.

This allows future Train/PK/Buff development to resolve static skill identity/target/range/property without reopening Config.

## Materialized Pet / Spirit data

`database/static/pets/` now contains:

- **8,349** Pets in compact indexes and full chunks.
- **1,889** Spirits in compact index and full chunks.
- PetFeatures, PetEquips, PetEquipSets, SpiritFeatures.

## PC input

`database/PC_INPUT_KEY_BINDINGS.csv` contains all **22** frozen PC key-binding records.

This is complementary to `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`; semantic Game/UI actions remain preferred over simulated physical input.

## Why both indexes and full chunks exist

The repository now intentionally preserves both:

```text
small index -> fast AI lookup
full chunk -> lossless deeper row data when needed
```

This avoids two bad extremes:

1. keeping only schemas/counts and forcing future AI to decrypt Config again;
2. loading all 22,763 Equip or 17,121 Monster rows into every context.

## Evidence boundaries remain unchanged

- Static Config/database = template/configured truth.
- Shipped Lua = client flow/action-construction truth.
- Native/runtime metadata = executable/runtime semantic evidence.
- Current runtime/server state = current spawn, mutable instance, dialog selection, acceptance and completion truth.

The database is now materially complete for the frozen Config domains relevant to the tool. Remaining gaps in `research/AUTO_RUNTIME_PROOF_QUEUE.md` are runtime/server proofs, not missing static-table extraction.
