# Catalog 75 bảng dữ liệu Config đã giải mã

Status: **VERIFIED from decrypted `Config.unity3d` TextAssets**.

| TextAsset | Direct records | Nội dung/chìa khóa chính |
|---|---:|---|
| `Books` | 128 | books/skills by faction, ID, level |
| `RoleTitles` | 156 | titles, groups, points, duration |
| `WorldMap` | 72 | MapID, Name, Position, quick path |
| `Pets` | 8,349 | pet templates, growth/base stats, skills |
| `SkillProperties` | 2,044 | skill property definitions |
| `CharSkeletons` | 2 | male/female skeleton models |
| `Tasks` | 516 | task ID/type/rule/dialog/next/requirements |
| `CharShapeShiftings` | 1,889 | shape-shift models/icons |
| `BookLevelUpCost` | 9 | book level costs |
| `AnimatedTitles` | 34 | animated title assets |
| `PartialAdditiveLocations` | 28 | additive model locations |
| `Spirits` | 1,889 | spirit templates/model/skill capacity |
| `EquipEnhance` | 99 | enhance rate/cost/fallback/value |
| `Pneumas` | 3 | pneuma config/properties/usage |
| `CharFaces` | 464 | face ID/model/sex |
| `DailyActivityAward` | 2 | activity/lucky plate config |
| `EquipIdentifyValues` | 256 | identify rate/value |
| `MagicAtrributes` | 509 | effect symbols/descriptions, e.g. `magic_maxhp` |
| `EquipSets` | 272 | equipment sets |
| `Monsters` | 17,121 | monster template, AI, level, EXP, MaxHP, combat stats, skills |
| `PartialModelCutoutLocations` | 256 | model cutout locations |
| `CharFashionGems` | 48 | fashion-gem model/bone transforms |
| `Stickers` | 212 | stickers/animations |
| `PetAnimatedTitles` | 3 | pet title resources |
| `NameColors` | 49 | name colors by type |
| `Medicines` | 692 | medicine price/level/stack/sellable |
| `PublicMounts` | 37 | mount model/action sets |
| `GrowPoints` | 407 | gather points/life skill/quest requirements |
| `NPCs` | 1,003 | `ID`, `Name`, `ResName`, `Avarta` |
| `AutoSkills` | 300 | activation type/value/cooldown/SkillIDs |
| `Factions` | 17 | faction Books/F1/InitQuickSkills |
| `GemColors` | 951 | gem color/series rendering |
| `DartConfig` | 5 | dart config/growth/skills |
| `WeaponGemFxs` | 1,778 | weapon gem FX mapping |
| `PetEquips` | 70 | pet equipment templates |
| `EquipExtendedAttributes` | 29 | extended equip attributes |
| `RoleFeatures` | 8 | role appearance/features/costs |
| `SoulConfig` | 7 | soul level/growth/properties |
| `CharHairs` | 606 | hair models/colors/sex |
| `PetEquipSets` | 13 | pet equip sets |
| `UISounds` | 5 | UI sound mapping |
| `GuildConfig` | 14 | guild level/skill/donate config |
| `LoginMaps` | 4 | login/select/create role maps/camera |
| `Skills` | 2,091 | ActionID/style/faction/weapon/range/target/Property |
| `CharFashionOrnaments` | 61 | fashion ornaments |
| `RoleReputes` | 22 | reputation tables |
| `DragonTattooConfig` | 2 | dragon tattoo stars/properties |
| `SpiritFeatures` | 3 | spirit level/skill features |
| `SignetConfig` | 5 | signet groups/stages/growth |
| `WeaponVisualGemsFx` | 2,735 | weapon-visual gem FX mapping |
| `GuildTask` | 360 | guild task condition/type/description |
| `CharMounts` | 361 | mount variants |
| `CharWings` | 733 | wing models/levels/transforms |
| `CreatureSounds` | 595 | creature sounds |
| `PCInputKeyBinding` | 22 | PC key bindings/UI events |
| `Locations` | 1,847 | object/model locations — **not NPC map X/Y** |
| `CharAvartas` | 674 | avatar IDs/icons/sex |
| `EquipSculptures` | 31 | sculpture data |
| `ClothGemFxs` | 1 | cloth gem FX |
| `DefaultChar` | 21 | default appearance/gear data |
| `Activities` | 45 | activities type/duration/visibility |
| `ModelParameters` | 1,710 | model scale/camera/UI offsets |
| `Gems` | 1,154 | gem template/type/level/price |
| `Fxs` | 991 | FX resources/bones/animation/sound |
| `Items` | 5,238 | price/bound/sellable/stack/template data |
| `PetFeatures` | 11 | reborn/personality/savvy costs/rates |
| `CharSouls` | 22 | soul model IDs |
| `FuBenScenarios` | 19 | dungeon/gather map/NPC/X/Y/requirements/timeout |
| `Equips` | 22,763 | equipment Type/EquipPoint/level/faction/price/durability/star/buff |
| `AutoPath` | 1,618 | 924 NPCData + 506 NPC transitions + 165 portals + 23 item destinations |
| `EnchantSkills` | 3 | enchant skills |
| `CharWeapons` | 1,875 | weapon model mappings |
| `VoodooVase` | 3 | voodoo vase config |
| `AllyTitles` | 75 | ally title icon/border assets |
| `Maps` | 193 | ID/Name/ResName/Level/Type/ServerID/music/colors |

## Highest-value tables

`NPCs`, `Maps`, `AutoPath`, `Items`, `Equips`, `Skills`, `SkillProperties`, `AutoSkills`, `MagicAtrributes`, `Monsters`, `Factions`, `FuBenScenarios`.

## Coordinate rule

`AutoPath/NPCData` links NPC ID → MapID but has **no X/Y**. Use runtime `Game.GetNPCPosition(npcID)`; do not invent coordinates from static data.
