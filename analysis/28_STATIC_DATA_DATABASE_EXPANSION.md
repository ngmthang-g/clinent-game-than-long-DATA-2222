# Static data database expansion — Items / Skills / Magic / Monsters / Equips

Status: **VERIFIED from decrypted Config XML; derived counts/classification are explicitly described below.**

This phase identified and normalized the largest Config tables so future AI can answer automation-relevant data questions without reopening Unity bundles. **Important repository-state correction:** full normalized row chunks were generated during research, but the complete large CSV chunk sets are not currently committed under `database/static/...`. Do not claim a specific chunk exists until it is visible in the repository tree.

## Source tables and exact row counts

- `Items.xml` — **5,238** Item rows
- `Skills.xml` — **2,091** Skill rows
- `MagicAtrributes.xml` — **509** magic-attribute rows
- `Monsters.xml` — **17,121** Monster rows
- `Equips.xml` — **22,763** Equip rows.

## Items

Normalized fields identified during extraction:

`ID, Name, Icon, ItemLevel, RequireLevel, BoundMoney, BasePrice, SellPrice, Throwable, Sellable, Bound, Stack, MaxUsageTimes, DurationHour, ScriptID, TypeDesc, IDFamily10M, ExtraHint, Description`.

### Snapshot statistics

From the 5,238 rows:

- `Sellable=true`: **4,970**
- `Sellable=false`: **268**
- `Throwable=true`: **5,005**
- `Throwable=false`: **233**.

The numeric `IDFamily10M = floor(ID/10,000,000)` is a useful derived lookup aid because shipped Auto loot code itself uses this family split. It is not a replacement for semantic `Game.GetItemType` when runtime code needs the true type.

## Skills

Normalized fields identified:

`ID, Name, Type, Style, FactionID, BookID, CanDirectlyStudy, RequireLevel, RequireWeapon, IsDamageSkill, TargetType, CastRange, AttackRadius, ProgressTime, CooldownGroup, AnimationDuration, MissileSpeed, MissileCount, FixedHitRate, FixedCritRate, Property, Tag, Icon, ActionID, ShortDescription, Description`.

### Snapshot type counts

- Active: **1,014**
- Auto: **602**
- Passive: **361**
- SpiritActive: **80**
- PetActive: **34**.

### Major target-type counts

- Self: **1,005**
- Enemy: **838**
- Owner: **145**
- SelfAndAlly: **57**
- PeacePlayer: **41**
- EnemyPlayer: **5**.

These counts are useful for narrowing candidate support/attack skills without scanning all 2,091 rows manually.

## Magic attributes

All 509 rows were normalized conceptually as:

`Symbol, Description, IncludeSign`.

Examples include `magic_maxhp`, elemental attack/resistance/ignore-resistance families and many specialized combat/equipment properties. This table is the semantic dictionary for properties found in skill/equipment/buff data.

## Monsters

Normalized fields identified:

`ID, ResName, Name, Level, Type, MaxHP, Exp, PhysAtk, PhysDef, MagicAtk, MagicDef, Hit, Dodge, CritAtk, CritDef, MoveSpeed, elemental attack/resistance fields, Skills, AIID, Avarta, Scale`.

Snapshot monster-type distribution:

- Hater: **12,487**
- Boss: **3,579**
- Normal: **1,030**
- Static: **25**.

This establishes a real offline MonsterID/ResName/Name/Level/MaxHP/AI/skill source for Auto Train diagnostics once the required rows are materialized into queryable repository data.

## Equips — important distinction between Type and EquipPoint

`Equips.xml` has two different concepts that must not be confused.

### `Type`

This is a specific equipment form/category using `C_EquipType`, including:

- 0 LongBlade
- 1 Spear
- 2 Sword
- 3 DoubleSwords
- 4 Fan
- 5 Circle
- 6 Crossbow
- 7 Staff
- 8 Flute
- 10 Hat
- 11 Shoes
- 12 Gloves
- 13 Cloth
- 14 Cuff
- 15 Shoulderpad
- 16 Blade
- 17 Sickle
- 20 Necklace
- 21 Belt
- 22 Ring
- 23 Amulet
- 24 Fashion
- 41 Mount
- 55 Dart
- 56 Soul
- 57 DragonTattoo
- 58 HeroicOrder
- 59 Signet
- 100 Zither.

### `EquipPoint`

This is the equipment slot/position semantic used by `C_EquipPosition` and runtime equipment classification.

Exact frozen-client positions:

- 0 Weapon
- 1 Hat
- 2 Cloth
- 3 Gloves
- 4 Shoes
- 5 Belt
- 6 Ring
- 7 Necklace
- 8 Mount
- 11 Ring_2
- 12 Amulet
- 13 Amulet_2
- 14 Cuff
- 15 Shoulderpads
- 16 Fashion
- 17 Dart
- 18 Soul
- 19 DragonTattoo
- 20 HeroicOrder
- 21 Signet
- 22 WeaponVisual.

**For the user's “keep weapons, sell other equipment” policy, the important static slot identity is `EquipPoint == 0` = Weapon.**

The frozen `Equips.xml` contains **4,685 rows with EquipPoint=0**.

Do not infer “weapon” merely from `Type < 10` because additional weapon forms such as Blade/Sickle/Zither exist. Slot/semantic position is safer.

## Normalized Equip fields

Fields identified during extraction:

`ID, Name, Type, TypeName, EquipPoint, EquipPositionName, IsWeaponPosition, Icon, Level, FactionID, BoundRule, BasePrice, SellPrice, Durability, Identifiable, Star, BuffID, DurationHour, SetID, VisualID, BaseAttributes, ExtraHint, Description`.

Nested `<BaseAttribute Symbol=... Value=...>` nodes can be flattened into `BaseAttributes` as `symbol=value|...` for targeted inspection.

## Runtime rule remains stronger for mutable inventory

These static tables explain what a template **is**. A live bag action must still use runtime state:

- `dbItemData.ID` = instance ID
- `dbItemData.ItemID` = template ID
- `dbItemData.Position` = current slot
- `dbItemData.Site` = current container
- `Game.IsItemSellable(ItemID)` = current semantic sellability guard
- `Game.GetItemType/GetEquipType` = runtime semantic classification.

Do not sell directly from an offline static row without verifying the current live instance and current rules.

## Repository materialization state

Current truth:

- schemas/counts/statistics above are VERIFIED;
- map/NPC/packet and several smaller databases are already materialized elsewhere in `database/`;
- the **full large Items/Skills/Magic/Monsters/Equips row chunks are not currently committed** under `database/static/...`.

Planned query-oriented locations remain:

- `database/static/items/`
- `database/static/skills/`
- `database/static/magic/`
- `database/static/monsters/`
- `database/static/equips/`.

When these are materialized, use small indexes plus chunks. Do not make future AI load all 22,763 equips or 17,121 monsters into context.

Canonical current-state guidance:

- `database/static/README.md`
- `database/static/LOOKUP_GUIDE.md`
- `research/TODO.md`.

## Auto-tool priority

Do not materialize every field/table merely because it exists. For the automation tool, priority is:

1. Items/Equips fields needed for sell/keep/loot policy;
2. Skills fields needed for Auto Train/Buff target/range/cooldown/condition logic;
3. Monster identity fields needed for Train filtering/boss detection;
4. everything else only when a concrete automation feature requires it.