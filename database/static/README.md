# Static Config database — query-oriented storage

This directory is the planned home for large normalized tables extracted from the frozen client's verified 75-table `Config.unity3d` dataset.

## Current repository state

The **source tables, row counts, many schemas and many derived semantics are VERIFIED** in the knowledge base.

However, the full normalized row chunks for the biggest tables are **not currently present under `database/static/`**. Do not assume a chunk exists merely because a schema/count is documented.

Current canonical planning/evidence:

- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` — detailed schema for Items/Skills/Magic/Monsters/Equips.
- `analysis/32_CONFIG_DOMAIN_ATLAS.md` — all 75 Config tables grouped by subsystem/value.
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` — next high-value tables and preservation schemas.
- `research/TODO.md` — current database-expansion priorities.
- `LOOKUP_GUIDE.md` — index/chunk anti-overread design.

## Verified high-value source sizes

### Combat / skills

- Skills — 2,091
- SkillProperties — 2,044
- AutoSkills — 300
- MagicAtrributes — 509
- Factions — 17
- Books — 128
- BookLevelUpCost — 9.

### Inventory / equipment

- Items — 5,238
- Equips — 22,763
- Medicines — 692
- Gems — 1,154
- EquipSets — 272
- EquipEnhance — 99
- EquipIdentifyValues — 256
- EquipExtendedAttributes — 29.

### World / task

- Monsters — 17,121
- Tasks — 516
- GrowPoints — 407
- GuildTask — 360
- Activities — 45.

### Pet / Spirit

- Pets — 8,349
- PetFeatures — 11
- PetEquips — 70
- PetEquipSets — 13
- Spirits — 1,889
- SpiritFeatures — 3.

Maps/NPC/AutoPath/FuBen already have substantial dedicated databases elsewhere under `database/`, so they do not need to be duplicated here.

## Recommended layout

```text
database/static/
  skills/
    SKILL_INDEX.csv
    SKILLS_....csv
    SKILL_PROPERTIES_....csv
    AUTO_SKILLS.csv
    FACTIONS.csv
    BOOKS.csv
  items/
    ITEM_INDEX.csv
    ITEMS_....csv
    MEDICINES.csv
    GEMS_....csv
  equips/
    EQUIP_INDEX.csv
    EQUIPS_....csv
    EQUIP_SETS.csv
    EQUIP_*.csv
  monsters/
    MONSTER_INDEX.csv
    MONSTERS_....csv
  tasks/
    TASK_INDEX.csv
    TASKS_....csv
    GROW_POINTS.csv
    GUILD_TASKS.csv
    ACTIVITIES.csv
  pets/
    PET_INDEX.csv
    PETS_....csv
    PET_FEATURES.csv
    PET_EQUIPS.csv
  spirits/
    SPIRIT_INDEX.csv
    SPIRITS_....csv
  magic/
    MAGIC_ATTRIBUTES.csv
```

Exact file naming may change when the rows are materialized. The invariant is **small index -> one relevant chunk**, not the specific chunk size.

## Index design

Indexes should keep only routing/search fields plus `Chunk`.

Examples:

### Skill index

`ID,Name,FactionID,Type,TargetType,RequireLevel,CastRange,Property,Chunk`

### Item index

`ID,Name,TypeDesc,RequireLevel,Sellable,Throwable,BasePrice,Chunk`

### Equip index

`ID,Name,Type,EquipPoint,Level,FactionID,Star,SetID,IsWeaponPosition,Chunk`

### Monster index

`ID,Name,ResName,Level,Type,AIID,Chunk`

### Task index

`ID,Name,TaskType,NextTaskOrRelation,Chunk`

### Pet index

`ID,Name,Type,Level,ResName,PrimarySkillRefs,Chunk`

## Lossless preservation rule

When normalizing a Config XML table:

1. preserve exact original attribute names;
2. put common/high-value fields into explicit columns;
3. preserve currently-uninterpreted scalar fields in `ExtraFields` or a lossless companion representation;
4. preserve nested child nodes in a stable flattened/structured form;
5. keep inference labels separate from original values.

Do not discard a field merely because today's feature does not need it. The entire purpose of this database is to prevent future re-decryption/reparsing.

## Runtime/static boundary

Static rows describe templates/configuration. Live mutable actions still require current runtime/server state.

For inventory:

- static Item/Equip row -> template semantics;
- live `dbItemData.ID` -> current instance;
- live `ItemID` -> template link;
- live `Position/Site` -> current location;
- runtime `IsItemSellable/GetItemType/GetEquipType` -> action-time guard.

For skills:

- static Skills/Properties -> what the skill is;
- runtime abilities/cooldown/target/range/progress -> whether the current role can use it now.

For monsters/tasks/pets:

- static rows -> template/objective semantics;
- runtime world/session state -> current spawned/current-task/current-companion truth.

## Weapon rule

For static equipment:

`Equips.xml EquipPoint == 0` = Weapon.

Do not use `Type < 10` as a universal weapon test.

## AI rule

Large static databases are **lookup systems**, not mandatory context.

Future AI should:

```text
identify subsystem
 -> search small index
 -> open one relevant chunk/record
 -> open canonical analysis only if semantics need explanation
```

Never load all 22,763 equips, 17,121 monsters or 8,349 pets merely because the data exists.
