# Large Static Database Lookup Guide

Purpose: keep large template databases useful without forcing AI to read thousands of rows.

## Current source sizes

- Items: 5,238 rows
- Skills: 2,091 rows
- Magic attributes: 509 rows
- Monsters: 17,121 rows
- Equips: 22,763 rows

Schemas/counts are VERIFIED from decrypted Config and documented in `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`.

## Important repository-state note

The normalized large CSV chunks have been generated during research, but **the full chunk files are not yet present under this GitHub directory**. `research/TODO.md` tracks their upload as remaining work.

Do not pretend a missing chunk exists. Until uploaded, use the schema/counts already documented and perform targeted source re-materialization only when a concrete record is required and no existing database answers it.

## Planned query-oriented layout

Recommended structure after upload:

```text
database/static/
  items/
    INDEX.csv
    ITEMS_....csv
  skills/
    INDEX.csv
    SKILLS_....csv
  magic/
    MAGIC_ATTRIBUTES.csv
  monsters/
    INDEX.csv
    MONSTERS_....csv
  equips/
    INDEX.csv
    EQUIPS_....csv
```

Index files should be small and contain only routing fields, for example:

### Item index

`ID, Name, TypeDesc, Sellable, Throwable, Chunk`

### Skill index

`ID, Name, FactionID, Type, Style, TargetType, Chunk`

### Monster index

`ID, Name, ResName, Level, Type, Chunk`

### Equip index

`ID, Name, Type, EquipPoint, Level, FactionID, IsWeaponPosition, Chunk`

The index tells AI which chunk to open; it does not duplicate every descriptive field.

## Lookup protocol

1. Identify the lookup key: ID/name/category.
2. Read a small index, not all chunks.
3. Open only the routed chunk/rows.
4. For implementation, cross-check live runtime state before mutable action.

## Runtime/static boundary

Static data describes templates. It does not replace live runtime identity/state.

For inventory actions:

- static Item/Equip row -> template semantics;
- live `dbItemData.ID` -> current instance identity;
- live `ItemID` -> template link;
- live `Position/Site` -> current location;
- runtime `IsItemSellable/GetItemType/GetEquipType` -> action-time guards.

## Weapon rule

Static equipment weapon slot identity is:

`EquipPoint == 0`

Do not use `Type < 10` as a universal weapon test because Blade/Sickle/Zither and other weapon forms make that incomplete.

## AI rule

Never load 22,763 equips or 17,121 monsters into context merely because the database exists. Use indexes/chunks as a search system.