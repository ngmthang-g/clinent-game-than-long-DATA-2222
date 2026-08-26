# 42 — Tool-first data materialization 2026-08-26

Status: **generated from the verified frozen client Config/Interface sources**. Purpose is to materialize only high-value query data serving the automation tool, while preserving the repository's index-first/anti-overread design.

## Newly materialized domains

### FuBen / Boss
- `database/fuben/FUBEN_SCENARIOS.csv` — 19 scenarios
- `database/fuben/FUBEN_ENTRY_NPCS.csv` — 19 entry/gather NPC mappings
- `database/fuben/FUBEN_ACTIONS.csv` — 268 normalized actions
- `database/fuben/FUBEN_KILL_TARGETS.csv` — 72 Kill actions with configured Monster/template/boss evidence
- `database/static/monsters/BOSS_NAME_INDEX.csv` — 578 distinct names grouping 3,579 exact `Type=Boss` templates.

### Tasks
- `database/static/tasks/TASK_INDEX.csv` — 516 frozen task templates
- `database/static/tasks/TASK_OBJECTIVES.csv` — normalized nested objective records with JSON preservation of exact attributes
- existing task runtime semantics remain in `analysis/23_TASK_QUEST_AUTOMATION.md`.

### Inventory policy
- `database/static/items/ITEM_POLICY_EXCEPTIONS.csv` — high-risk/nonstandard keep-sell-drop candidates
- `database/static/items/ITEM_TYPE_COUNTS.csv` — TypeDesc distribution
- existing exact sell/runtime policy remains authoritative at mutation time.

### Skills
- `database/static/skills/SKILL_TOOL_INDEX.csv` — compact 2,091-row lookup for ID/name/faction/type/target/level/range/property.

### PC input
- `database/PC_INPUT_KEY_BINDINGS.csv` — 22 shipped key binding rows; presentation/input reference only, not preferred semantic action layer.

## What is deliberately not bulk committed

The decrypted Config can generate very large full-row datasets (22,763 Equips, 17,121 Monsters, 8,349 Pets, 5,238 Items, etc.). They should not all be shoved into AI context or duplicated merely because extraction is possible.

The rule remains:

`small index -> exact relevant record/chunk -> runtime state when mutable`.

Full local extraction is reproducible from the frozen snapshot, but GitHub materialization should prioritize tool features and add deeper chunks only when an actual feature needs fields absent from the compact index.

## Evidence boundaries

- Static Config = template/configured truth.
- Shipped Lua = client flow/action construction truth.
- Runtime/server state = current existence, state, acceptance, completion truth.
- Derived labels (for example name/step text suggesting boss) stay separate from exact `Monsters.Type=Boss` evidence.
