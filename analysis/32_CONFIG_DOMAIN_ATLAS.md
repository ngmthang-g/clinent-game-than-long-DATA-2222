# Config Domain Atlas — 75 decrypted client tables grouped by subsystem

Status: **VERIFIED at table-name / row-count / high-level field-semantic level from decrypted `Config.unity3d`; domain grouping and tool-value ranking are analytical organization, not new runtime proof.**

Purpose: future AI should not treat the 75 Config TextAssets as one flat pile. This atlas groups them by gameplay domain, explains what each group can answer, and tells the AI when static data is sufficient versus when runtime/Lua evidence is still required.

Canonical raw catalog: `database/CONFIG_TABLE_CATALOG.md`.

---

## Tier S — highest reverse/build value

These tables directly answer questions required by automation, runtime state interpretation, routing, combat, inventory or service discovery.

### World / map / NPC / routing

| Table | Rows | What it gives | Build value |
|---|---:|---|---|
| `Maps` | 193 | Map ID/name/resource/type/server/music/color metadata | canonical MapID dictionary |
| `WorldMap` | 72 | world-map positions / quick-path presentation data | map UI / travel hints |
| `NPCs` | 1,003 | NPC `ID`, `Name`, `ResName`, avatar identity | NPC semantic identity |
| `AutoPath` | 1,618 | NPC associations, NPC-mediated transitions, portals, item destinations | route graph / destination lookup |
| `FuBenScenarios` | 19 | dungeon/scenario map, NPC, X/Y, requirements, timeout | dungeon automation context |
| `Monsters` | 17,121 | monster IDs/names/levels/MaxHP/AI/stats/skills | target identity, quest/FuBen/Train diagnostics |
| `GrowPoints` | 407 | gather-point/life-skill/quest requirements | gather automation / world-object taxonomy |

Important boundary:

- static `NPCs` + `AutoPath` can map NPC identity to map association;
- they **do not prove live NPC X/Y**;
- prefer runtime `Game.GetNPCPosition(npcID)` and `Game.GoTo(...)` for actual execution.

### Combat / skill / buff

| Table | Rows | What it gives | Build value |
|---|---:|---|---|
| `Skills` | 2,091 | skill identity, style, faction, weapon requirement, target type, range, cooldown group, action, descriptions | core combat/support skill DB |
| `SkillProperties` | 2,044 | skill-property definitions | decode skill behavior beyond display name |
| `AutoSkills` | 300 | activation type/value/cooldown/SkillIDs | built-in automatic skill policy clues |
| `MagicAtrributes` | 509 | property symbol dictionary such as `magic_maxhp` | semantic interpretation of buff/equip/skill properties |
| `Books` | 128 | books/skills by faction, ID, level | skill progression / faction skill tree |
| `Factions` | 17 | faction books/F1/initial quick skills | faction bootstrap / default skill identity |
| `EnchantSkills` | 3 | enchant skill definitions | narrow special-skill subsystem |

Static data answers what a skill template **is**. Runtime still decides whether a live role currently owns it, can cast it, has target/range/cooldown/progress restrictions, etc.

### Inventory / item / equipment / economy

| Table | Rows | What it gives | Build value |
|---|---:|---|---|
| `Items` | 5,238 | item template, sellable/throwable/stack/price/binding metadata | item policy / Auto Sell / loot filters |
| `Equips` | 22,763 | equip subtype, `EquipPoint`, faction, level, price, durability, star, buff, attributes | gear classification / keep-sell policy |
| `Medicines` | 692 | medicine price/level/stack/sellability | recovery consumables / item-use policy |
| `Gems` | 1,154 | gem type/level/price | gem classification |
| `EquipSets` | 272 | equipment set membership | keep/set detection |
| `EquipEnhance` | 99 | enhance rate/cost/fallback/value | enhancement calculations / UI explanation |
| `EquipIdentifyValues` | 256 | identify rates/values | unidentified gear semantics |
| `EquipExtendedAttributes` | 29 | extended equip attributes | equip property decoding |
| `PetEquips` | 70 | pet-equipment templates | pet inventory classification |
| `PetEquipSets` | 13 | pet equipment sets | pet gear set identity |

Critical runtime distinction remains:

`ID = live instance` != `ItemID = template` != `Position = slot` != `Site = container`.

Never issue a live mutation directly from an offline row without re-resolving the current instance/state.

---

## Tier A — major feature-enabling domains

### Pet / Spirit / companion systems

| Table | Rows | Meaning / likely use |
|---|---:|---|
| `Pets` | 8,349 | pet templates, growth/base stats, skills |
| `PetFeatures` | 11 | reborn/personality/savvy costs/rates |
| `PetEquips` | 70 | pet equipment templates |
| `PetEquipSets` | 13 | pet gear sets |
| `PetAnimatedTitles` | 3 | pet title resources |
| `Spirits` | 1,889 | spirit templates/model/skill capacity |
| `SpiritFeatures` | 3 | spirit level/skill features |

These tables can turn the already-documented runtime Pet/Spirit state into a proper template DB: live Pet ID/skill/state -> static name/growth/skill/equipment semantics.

### Task / activity / progression

| Table | Rows | Meaning / likely use |
|---|---:|---|
| `Tasks` | 516 | task ID/type/rule/dialog/next/requirements |
| `GuildTask` | 360 | guild task condition/type/description |
| `Activities` | 45 | activity type/duration/visibility |
| `DailyActivityAward` | 2 | activity/lucky-plate award config |
| `RoleReputes` | 22 | reputation tables |
| `RoleTitles` | 156 | title group/points/duration |
| `AnimatedTitles` | 34 | animated title assets |
| `AllyTitles` | 75 | ally title icon/border assets |

`Tasks` is especially valuable because `analysis/23_TASK_QUEST_AUTOMATION.md` already proves built-in Auto Quest consumes structured task data. A normalized task DB would let AI answer task type / objective / NPC / next-step questions without reopening Config.

### Guild / faction / social progression

| Table | Rows | Meaning / likely use |
|---|---:|---|
| `GuildConfig` | 14 | guild level/skill/donation config |
| `GuildTask` | 360 | guild tasks |
| `Factions` | 17 | faction books/F1/initial quick skills |
| `Books` | 128 | faction skill books |
| `BookLevelUpCost` | 9 | book-level costs |

This group is suitable for future faction-aware Auto Buff/skill selection and guild task/progression helpers. Do not infer live guild membership/permission from static config; runtime role/team/guild state remains authoritative.

---

## Tier B — useful support / presentation / configuration domains

### Character appearance / equipment visuals

- `CharFaces` — 464
- `CharHairs` — 606
- `CharAvartas` — 674
- `CharMounts` — 361
- `CharWings` — 733
- `CharWeapons` — 1,875
- `CharShapeShiftings` — 1,889
- `CharFashionOrnaments` — 61
- `CharFashionGems` — 48
- `CharSouls` — 22
- `DefaultChar` — 21
- `RoleFeatures` — 8
- `PublicMounts` — 37
- `DartConfig` — 5
- `SoulConfig` — 7
- `DragonTattooConfig` — 2
- `SignetConfig` — 5

These are useful for displaying/identifying visual state, cosmetic/equipment categories, mount/wing/soul/signet subsystems and explaining IDs seen at runtime. They are usually lower priority for core Auto Train/Buff/Sell unless the tool adds appearance or equipment-inspection features.

### Model / FX / audio / rendering support

- `ModelParameters` — 1,710
- `Locations` — 1,847
- `PartialAdditiveLocations` — 28
- `PartialModelCutoutLocations` — 256
- `WeaponGemFxs` — 1,778
- `WeaponVisualGemsFx` — 2,735
- `ClothGemFxs` — 1
- `Fxs` — 991
- `CreatureSounds` — 595
- `UISounds` — 5
- `GemColors` — 951
- `CharSkeletons` — 2
- `EquipSculptures` — 31
- `Stickers` — 212
- `NameColors` — 49

These tables mostly explain presentation/resource binding. They may help identify model/FX IDs or debug UI visualization, but should not distract feature AI from semantic gameplay sources.

### Input / login / client presentation

- `PCInputKeyBinding` — 22
- `LoginMaps` — 4

`PCInputKeyBinding` is useful for understanding default keyboard-to-UI bindings, but physical keys should not replace semantic internal actions when semantic APIs exist.

---

## Tier C — narrow/specialized subsystems

- `Pneumas` — 3
- `VoodooVase` — 3

They may become important if a future tool feature explicitly targets those systems. Until then they should remain lookup-only.

---

## Cross-table joins future AI should prefer

### Skill identity / support logic

```text
Faction
 -> Factions
 -> Books
 -> Skills
 -> SkillProperties
 -> MagicAtrributes
```

Use runtime `GetAbilities`, `CanUseSkill`, `GetSkillCooldown`, `GetBuffs` as live truth.

### Live item / equipment interpretation

```text
live dbItemData.ItemID
 -> Items
 -> if equip: Equips
 -> MagicAtrributes / EquipExtendedAttributes / EquipSets as needed
```

Use live instance `dbItemData.ID` for mutation requests.

### Monster / quest target interpretation

```text
Task objective ID
 -> Tasks
 -> Monster/NPC/GrowPoint template
 -> Map/AutoPath destination hints
```

Use runtime world objects and map-ready state for execution.

### Pet / Spirit interpretation

```text
live Pet/Spirit state
 -> Pets / Spirits
 -> PetFeatures / SpiritFeatures
 -> pet skills/equipment tables as needed
```

### NPC service investigation

```text
NPC ID
 -> NPCs identity
 -> AutoPath map association
 -> runtime GetNPCPosition
 -> Game.ClickNPC
 -> server GameDialog.Selections
 -> service-specific UI/packet state
```

Static `ResName` may make a service a strong candidate, but does not itself prove the server service contract.

---

## Static vs runtime authority rule

### Static Config is authoritative for

- template identity;
- names/descriptions;
- configured level/faction/type/range/price/slot relations;
- pre-shipped route/scenario definitions;
- classification dictionaries.

### Runtime/Lua/server state is authoritative for

- current character state;
- current item instance/site/slot;
- current NPC dialog selections;
- current cooldown/buff/progress state;
- current world object position/existence;
- current shop/team/task/session state;
- success/failure of mutations.

Never let a static table override live server-authoritative state.

---

## Data extraction priority from here

If expanding the machine-readable database, prioritize in this order:

1. `Skills` + `SkillProperties` + `AutoSkills` + `Factions` + `Books`;
2. `Items` + `Equips` + `Medicines` + equipment support tables;
3. `Tasks` + `GrowPoints` + activity/guild-task tables;
4. `Pets` + `PetFeatures` + `Spirits` + companion equipment;
5. cosmetics/rendering only when a concrete tool feature requires them.

This order maximizes build value while keeping AI context small.
