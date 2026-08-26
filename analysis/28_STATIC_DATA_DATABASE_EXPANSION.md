# 28 — Static data database expansion — current status

Status: **COMPLETED for the frozen snapshot.** This document originally planned normalization of the largest Config tables. That work is now materialized on `main`; the old statement that large chunks were not committed is obsolete.

Canonical lookup entrypoint:

`database/TOOL_DATA_INDEX.md`

Generated-data manifest:

`database/TOOL_DATA_MATERIALIZATION_MANIFEST.csv`

All-75-table fallback catalog:

`database/config_full/CONFIG_FULL_CATALOG.csv`

Generators:

- `tools/materialize_tool_data.py` — tool-first semantic/index databases.
- `tools/materialize_all_config.py` — structurally-lossless fallback for every recovered Config XML table.

## Materialized high-value tables

### Items

Frozen rows: **5,238**.

Primary paths:

- `database/static/items/ITEM_TOOL_INDEX.csv`
- `database/static/items/ITEM_INDEX.csv`
- `database/static/items/ITEMS_*.csv`
- `database/static/items/ITEM_POLICY_EXCEPTIONS.csv`
- `database/static/items/MEDICINES.csv`
- `database/static/items/GEMS_*.csv`

Verified frozen statistics retained from the original analysis:

- Sellable=true: 4,970
- Sellable=false: 268
- Throwable=true: 5,005
- Throwable=false: 233.

Runtime mutation still uses current live item instance ID, not template ItemID alone.

### Skills / Magic

Frozen rows:

- Skills: **2,091**
- SkillProperties: **2,044**
- AutoSkills: **300**
- MagicAttributes: **509**.

Primary paths:

- `database/static/skills/SKILL_TOOL_INDEX.csv`
- `database/static/skills/SKILL_INDEX.csv`
- `database/static/skills/SKILLS_*.csv`
- `database/static/skills/SKILL_PROPERTIES_*.csv`
- `database/static/skills/AUTO_SKILLS.csv`
- `database/static/magic/MAGIC_ATTRIBUTES.csv`.

Static skill identity/range/target/property is template truth. Current ownership, cooldown, target legality and server acceptance remain runtime truth.

### Monsters / Bosses

Frozen Monster templates: **17,121**.

Type distribution from the frozen data:

- Hater: 12,487
- Boss: **3,579**
- Normal: 1,030
- Static: 25.

Primary paths:

- `database/static/monsters/MONSTER_INDEX_*.csv`
- `database/static/monsters/BOSS_INDEX_*.csv`
- `database/static/monsters/BOSS_NAME_INDEX.csv` — 578 grouped Boss names.

Current spawned actor/RoleID/position/death state remains runtime-authoritative.

### Equips

Frozen rows: **22,763**.

Primary paths:

- `database/static/equips/EQUIP_INDEX_*.csv`
- `database/static/equips/EQUIPS_*.csv`
- `database/static/equips/WEAPON_INDEX.csv`
- `database/static/equips/EQUIP_POSITION_TYPE_COUNTS.csv`.

Hard rule preserved:

```text
EquipPoint == 0 = weapon position
```

Do not use `Type < 10` as a universal weapon test.

## Storage model now in force

Future AI should use:

```text
feature/question
 -> small tool/domain index
 -> one exact row/chunk
 -> canonical analysis if semantic context is required
 -> fresh runtime/server state for mutable action
```

Do not load all large tables into context.

If a field is absent from the tool-first compact index, use the corresponding full static chunk. If the feature reaches a Config domain that does not have a specialized tool-first index, use `database/config_full/<Table>/ROWS_*.csv` instead of decrypting `Config.unity3d` again.

## Historical note

This file is retained because its row counts/classification findings were part of the research sequence. Its former "not currently committed" planning state is superseded by the actual generated tree and manifests above.
