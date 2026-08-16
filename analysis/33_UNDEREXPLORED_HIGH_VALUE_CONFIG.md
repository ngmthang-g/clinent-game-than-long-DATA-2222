# Underexplored High-Value Config — next data to normalize, not broad reverse

Status: **VERIFIED table existence/counts from decrypted Config; proposed extraction schemas and expected build value are analysis/planning.**

Purpose: the client has already been broadly reverse-engineered. The remaining data work should focus on Config tables that can answer future build questions directly but are not yet represented as compact machine-readable databases in GitHub.

This document deliberately avoids reopening unrelated binaries.

---

## Priority 1 — Skills semantic stack

### `Skills` — 2,091 rows

Already known high-value fields include:

`ID, Name, Type, Style, FactionID, BookID, CanDirectlyStudy, RequireLevel, RequireWeapon, IsDamageSkill, TargetType, CastRange, AttackRadius, ProgressTime, CooldownGroup, AnimationDuration, MissileSpeed, MissileCount, FixedHitRate, FixedCritRate, Property, Tag, Icon, ActionID, ShortDescription, Description`.

Future normalized lookup should support:

- skill by ID/name;
- faction -> skill list;
- support-vs-damage filtering;
- target type (`Self`, `SelfAndAlly`, `PeacePlayer`, `Enemy`, etc.);
- cast range / progress / cooldown grouping;
- weapon requirement;
- skill -> property join.

Do not infer current ownership/readiness from static rows. Runtime `GetAbilities`, `CanUseSkill`, `GetSkillCooldown` remains authoritative.

### `SkillProperties` — 2,044 rows

This is one of the most valuable still-underused tables because the main `Skills` row often points to a property definition rather than fully explaining all effects.

Extraction goal:

```text
PropertyID / key
all direct scalar attributes
all nested effect/property references
all MagicAttribute symbols
conditional/target-related fields
```

Future AI should be able to answer:

```text
SkillID
 -> Skills.Property
 -> SkillProperties
 -> MagicAtrributes.Description
```

without rereading XML.

### `AutoSkills` — 300 rows

Verified catalog semantics: activation type/value/cooldown/SkillIDs.

Likely high build value:

- understand shipped automatic-skill triggers;
- distinguish low-HP / timing / state-driven automatic behavior;
- recover reusable policy without reproducing UI automation.

Required normalized columns should preserve every activation/condition field verbatim because enum meaning may need later cross-reference.

Do not rename numeric activation types into human semantics unless Lua/Config cross-check proves the mapping.

### `Factions` — 17 rows

Verified catalog semantics include Books/F1/InitQuickSkills.

Normalize at minimum:

```text
FactionID
Name if present
Book references
F1/default skill references
initial quick-skill references
all unrecognized fields preserved
```

This can make faction-specific skill setup and Nga My/support discovery much easier.

### `Books` — 128 rows / `BookLevelUpCost` — 9 rows

Join chain:

```text
Faction -> Book -> Skill(s) -> Level/Cost
```

Useful for skill progression and explaining why a skill exists but is not yet available.

---

## Priority 2 — Item/equipment policy stack

### `Items` — 5,238 rows

Normalized schema is already documented. GitHub should eventually contain queryable chunks/indexes for:

- sellable/throwable;
- stack size;
- price;
- required level;
- script/medicine/equipment/gem identity;
- descriptions/search text.

For Auto Sell, static `Sellable=true` is a candidate-policy input only. Runtime `Game.IsItemSellable(ItemID)` and live instance state remain the final guard.

### `Equips` — 22,763 rows

Critical preserved truth:

`EquipPoint == 0` = Weapon.

Do not simplify weapon classification to `Type < 10` because additional weapon subtypes exist.

Useful query indexes:

```text
ID -> Name/Type/EquipPoint/Level/Faction/Star/SellPrice
Faction + EquipPoint + level range
IsWeaponPosition
SetID
BuffID
BaseAttributes symbols
```

### `Medicines` — 692 rows

This table deserves its own normalized database because medicine/recovery behavior is a common automation feature.

Verified high-level fields from catalog: medicine price/level/stack/sellability.

Extraction should preserve:

- medicine/template ID;
- name;
- level/requirement;
- stack;
- price/sellability;
- all effect/script references;
- all timing/cooldown/use-condition fields if present.

Then join with `Items` and runtime bag instances.

### Equipment support tables

Normalize when equipment intelligence becomes a feature:

- `EquipSets` — 272
- `EquipEnhance` — 99
- `EquipIdentifyValues` — 256
- `EquipExtendedAttributes` — 29

These can support smarter keep/sell decisions, but only after the basic Item/Equip index exists.

---

## Priority 3 — Tasks / gathering / activities

### `Tasks` — 516 rows

Verified catalog semantics:

`task ID/type/rule/dialog/next/requirements`.

The shipped client already has structured Auto Quest logic. A normalized task DB can make task automation explainable instead of opaque.

Recommended schema preserves:

```text
TaskID
Name/title if present
TaskType
requirements
pre/next task references
NPC/object/monster/item parameters
map/destination references
dialog text/references
reward references
all raw parameter arrays/strings
```

Do not discard “unknown” parameter columns; many task engines encode type-specific semantics positionally.

### `GrowPoints` — 407 rows

Verified semantics: gather point / life skill / quest requirements.

Useful joins:

```text
Task objective
 -> GrowPoint template
 -> nearby world object
 -> path / click object
```

Potential tool features:

- gather-object identification;
- life-skill target filters;
- quest objective explanation.

### `Activities` — 45 / `DailyActivityAward` — 2

These are useful for activity availability/display timing and reward UI context.

Treat configured duration/visibility as client configuration, not proof that a server event is currently open.

### `GuildTask` — 360

Useful for guild task type/condition/description lookup. Execution still needs actual current task state and exact action semantics.

---

## Priority 4 — Pet / Spirit template intelligence

### `Pets` — 8,349 rows

This is one of the largest non-monster tables and can substantially improve future Pet automation/inspection.

Verified catalog semantics:

`pet templates, growth/base stats, skills`.

Recommended normalized fields:

```text
ID
Name
ResName/model
level/tier/type
base HP/attack/defense/growth fields
personality/reborn/savvy references
skill IDs / skill slots
visual/avatar fields
all uncommon raw attributes
```

Do not assume every row is a player-ownable pet; preserve category/type fields so later AI can separate templates safely.

### `PetFeatures` — 11

Verified semantics: reborn/personality/savvy costs/rates.

This small table should be normalized in full rather than summarized.

### `PetEquips` — 70 / `PetEquipSets` — 13

Useful for pet gear classification, set recognition and future keep/store/sell rules.

### `Spirits` — 1,889 / `SpiritFeatures` — 3

Can join live Spirit state from `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` to static template/skill capacity/feature progression.

---

## Priority 5 — Guild / role progression

### `GuildConfig` — 14

Verified semantics: guild level/skill/donation config.

Small enough that the ideal database is a full normalized table, not prose only.

### `RoleReputes` — 22

Useful for reputation threshold/name/reward interpretation.

### `RoleTitles` — 156

Useful for title group/points/duration and explaining title IDs seen at runtime.

These are useful for management/inspection features but lower priority than combat/inventory/task data.

---

## Priority 6 — PC/client semantics

### `PCInputKeyBinding` — 22

This table should be extracted because the snapshot is a Windows client and it can explain:

- default PC hotkeys;
- which visible UI action a key maps to;
- why physical F-key behavior differs from semantic skill identity.

But it must be treated as **input presentation**, not the preferred automation action layer.

### `LoginMaps` — 4

Useful only for login/create/select-role scene understanding.

---

## Index-first storage design

Large datasets should not be dumped into one giant AI document.

Recommended pattern:

```text
database/static/skills/SKILL_INDEX.csv
database/static/skills/SKILLS_0001_0500.csv
...

database/static/pets/PET_INDEX.csv
database/static/pets/PETS_0001_1000.csv
...
```

Index rows should contain only high-search-value columns plus a `Chunk` field.

Example Skill index:

```text
ID,Name,FactionID,Type,TargetType,RequireLevel,CastRange,Property,Chunk
```

Example Pet index:

```text
ID,Name,Type,Level,ResName,PrimarySkillIDs,Chunk
```

AI locates a record in the small index, then opens exactly one chunk.

---

## Preservation rule for unknown columns

When extracting XML, do not throw away fields merely because their meaning is unknown today.

For each table:

1. keep a normalized high-value CSV;
2. preserve unrecognized scalar attributes in an `ExtraFields` JSON/string column or a lossless raw-row companion;
3. preserve nested child nodes in a structured flattened representation;
4. label inferred field semantics separately from exact attribute names.

This prevents future AI from having to decrypt/reparse the bundle again just because one currently-unused attribute becomes important.

---

## What not to do next

Do not spend the next phase broadly disassembling UnityPlayer, baselib, LiveKit or graphics libraries.

For tool-building knowledge, the highest remaining value is **normalizing the already-decrypted semantic Config/Lua data**, especially Skills/SkillProperties/AutoSkills, Items/Equips/Medicines, Tasks/GrowPoints and Pets/Spirits.
