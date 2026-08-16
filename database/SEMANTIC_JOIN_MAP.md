# Semantic Join Map — how client data sources connect

Purpose: future AI often knows one ID but needs to know **which other table/runtime source to join next**. This file records the safest join paths without forcing AI to read all Config tables.

Evidence labels:

- **VERIFIED JOIN** — both sides and the relationship are directly established by extracted fields/runtime usage.
- **STRONG JOIN CANDIDATE** — field names/table semantics strongly indicate the relation, but full row-by-row validation has not been committed.
- **TYPE-SPECIFIC / RUNTIME** — relationship depends on objective/type/server state; do not treat as one universal static foreign key.

---

## 1. Runtime live item -> static template

### VERIFIED JOIN

```text
live dbItemData.ItemID
 -> static item/equipment template identity
```

Runtime live object also keeps:

```text
dbItemData.ID       = live instance ID
dbItemData.ItemID   = template ID
dbItemData.Position = current slot
dbItemData.Site     = current container
```

Use current instance `ID` for mutations such as sell/move.

### Template interpretation layers

```text
ItemID
 -> Items
 -> if equipment: Equips
 -> optional EquipSets / enhancement / identify / extended attributes
```

The client itself exposes `GetItemTemplateData`, `GetItemType`, `GetEquipType`, so runtime semantic APIs remain the safest action-time classifier.

---

## 2. Equipment template -> equipment semantics

### VERIFIED FIELD SEMANTICS

`Equips` contains:

- `ID`
- `Type`
- `EquipPoint`
- `FactionID`
- `Level`
- `Star`
- `BuffID`
- `SetID`
- `BaseAttributes` and other fields.

Exact important rule:

```text
EquipPoint == 0 -> Weapon
```

### STRONG JOIN CANDIDATES

```text
Equips.SetID
 -> EquipSets

Equips.BaseAttributes.Symbol
 -> MagicAtrributes.Symbol

Equips.BuffID
 -> runtime/static buff-related definitions where the same BuffID is used
```

Do not assume every nonzero SetID/BuffID resolves until the actual normalized rows are cross-checked.

---

## 3. SkillID -> skill template -> property semantics

### VERIFIED JOIN ROOT

Runtime APIs use `skillID`, and `Skills.xml` provides static rows keyed by skill `ID`.

```text
runtime SkillID
 -> Skills.ID
```

Use this for:

- name;
- faction;
- target type;
- cast range;
- cooldown group;
- weapon/level requirements;
- property/action metadata.

### STRONG JOIN CANDIDATE

```text
Skills.Property
 -> SkillProperties
```

Reason: `Skills` explicitly contains a `Property` field and the extracted Config contains a dedicated `SkillProperties` table with 2,044 rows.

This is one of the highest-value joins to validate/normalize row-by-row.

### Strong property-symbol interpretation

```text
SkillProperties magic/effect Symbol
 -> MagicAtrributes.Symbol
 -> MagicAtrributes.Description
```

`MagicAtrributes` is the semantic dictionary for `magic_*` properties. Preserve raw symbols even when a human description is incomplete.

---

## 4. Skill -> faction / book progression

`Skills` contains `FactionID` and `BookID`.

Config also contains:

- `Factions` — 17 rows;
- `Books` — 128 rows;
- `BookLevelUpCost` — 9 rows.

### STRONG JOIN CANDIDATES

```text
Skills.FactionID
 -> Factions.ID / faction identity

Skills.BookID
 -> Books.ID

Books faction/level references
 -> Factions / BookLevelUpCost
```

`Factions` is known to contain Books/F1/InitQuickSkills relationships, making this stack especially valuable for faction-specific skill discovery.

Do not invent the exact key column names in Factions/Books until the normalized rows preserve them.

---

## 5. AutoSkills -> Skills

`AutoSkills` contains activation type/value/cooldown/SkillID semantics.

### STRONG JOIN CANDIDATE

```text
AutoSkills SkillID(s)
 -> Skills.ID
```

Use case:

```text
automatic trigger definition
 -> actual skill template
 -> target/range/property semantics
```

Do not rename activation type numeric values into guessed meanings without a Lua/Config usage cross-check.

---

## 6. Runtime buff -> buff/property semantics

### VERIFIED RUNTIME ROOT

`Game.GetBuffs()` exposes:

- BuffID
- DurationTick
- Stack.

`Game.GetBuffData(BuffID)` and `Game.GetBuffProperties(BuffID)` expose richer semantic data.

### Potential static interpretation

`MagicAtrributes` provides property-symbol meanings used by buff/skill/equipment semantics.

The exact static BuffID -> dedicated Config row relation is not yet represented as one normalized canonical table in the KB.

Rule:

- use runtime BuffID/properties as current truth;
- use static/magic tables only to interpret known symbols/relationships;
- do not manufacture a nonexistent `Buffs.csv` relation.

---

## 7. NPCID -> NPC identity -> map association -> live coordinate

### VERIFIED JOIN

```text
NPC ID
 -> NPCs.ID
 -> Name / ResName / Avarta
```

### VERIFIED static map association for many NPCs

```text
AutoPath.NPCData NPCID
 -> NPCs.ID
AutoPath.NPCData MapID
 -> Maps.MapID
```

### Runtime coordinate authority

Static NPCData does **not** provide the normal live NPC X/Y.

Use:

```text
NPCID
 -> Game.GetNPCPosition(npcID)
 -> live X/Y
```

Then `Game.GoTo` / `ClickNPC`.

### Service layer

```text
NPC Name / ResName
 -> offline service candidate tag
 -> runtime GameDialog / NPCShop data
 -> VERIFIED service only after actual runtime evidence
```

Candidate tags are in `database/NPC_SERVICE_CANDIDATES.md`.

---

## 8. MapID -> map template / route graph

### VERIFIED JOIN

```text
MapID
 -> Maps.csv
```

### Route topology

Extracted AutoPath relations:

```text
portal FromMapID/ToMapID
 -> Maps

NPC-mediated transition MapIDs
 -> Maps
```

Databases:

- `AUTOPATH_PORTAL_EDGES.csv`
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- `AUTOPATH_ITEM_DESTINATIONS.csv`.

Static graph is topology/diagnostic data. Runtime `Game.GoTo` remains preferred executor because edge availability may depend on level/quest/event/state.

---

## 9. FuBen scenario -> map / NPC / runtime dungeon state

`FuBenScenarios` contains 19 verified definitions with map, gather/NPC/coordinates, player/level/timeout-style requirements.

### VERIFIED/STRUCTURAL joins

```text
scenario MapID
 -> Maps

scenario NPC reference
 -> NPCs
```

Runtime dungeon state additionally comes from AutoFight_FuBen and FuBen packet/event data.

Static scenario definition is not proof that the dungeon is currently open/entered.

---

## 10. Task -> objective template

`Tasks` contains 516 rows with task ID/type/rule/dialog/next/requirements semantics.

Built-in Auto Quest uses type-specific task parameters.

### TYPE-SPECIFIC / RUNTIME joins

Depending on `TaskType`, task parameters may refer to:

```text
NPC ID       -> NPCs
Monster ID   -> Monsters
Item ID      -> Items
GrowPoint ID -> GrowPoints
Map/area     -> Maps / runtime position
```

Do **not** treat one positional task parameter as the same foreign key for every TaskType.

Normalization must preserve:

- TaskType;
- raw parameter arrays/strings;
- exact parameter order;
- any known type-specific interpretation.

Only then should per-type joins be promoted to VERIFIED.

---

## 11. Runtime monster -> static Monsters

`Monsters` contains 17,121 templates with IDs, names, ResName, level, MaxHP, combat stats, skills and AIID.

### Strong runtime join model

```text
runtime monster/object template identity
 -> Monsters.ID
 -> static name/level/stats/AI/skills
```

Current spawned HP/position/death state comes from runtime/AOI data, not the static row.

Do not use static MaxHP as current HP.

---

## 12. GrowPoint -> task / runtime gather object

`GrowPoints` has 407 rows.

### TYPE-SPECIFIC join

```text
Task gather objective
 -> GrowPoints template
 -> runtime nearby GrowPoint/world object
 -> path/interact
 -> progress/event proof
```

Exact object field mapping should be done only when a gather feature needs it.

---

## 13. Runtime Pet -> `Pets`

`Pets` contains 8,349 templates; runtime Pet state is already exposed/documented.

### STRONG JOIN CANDIDATE

```text
runtime Pet template/ID reference
 -> Pets.ID
 -> static name/model/growth/base stats/skill references
```

Companion tables:

```text
Pet feature/progression
 -> PetFeatures
Pet equipment
 -> PetEquips
Pet set identity
 -> PetEquipSets
```

Exact key fields should be preserved during normalization rather than guessed from table names alone.

---

## 14. Runtime Spirit -> `Spirits`

`Spirits` contains 1,889 templates; `SpiritFeatures` contains 3 rows.

### STRONG JOIN CANDIDATE

```text
runtime Spirit template identity
 -> Spirits.ID
 -> model / skill-capacity / other static semantics
```

Skill references may join to `Skills`, but this relation should be row-validated before being labeled universal.

---

## 15. Live ground item -> Items / Equips

Built-in loot flow receives item-pack contents and has ItemIDs/slots suitable for policy.

Useful join:

```text
pack item ItemID
 -> Items
 -> if Equip -> Equips
 -> filter by sell/quality/star/type policy
```

After pickup, the item becomes a normal live bag instance with a new/current `dbItemData.ID`.

Do not reuse ground-pack slot identity as a bag instance identity.

---

## 16. Role FactionID -> Factions / Skills

Nearby/local/selected role state exposes FactionID.

Static Config has Factions and Skills.FactionID.

Useful interpretation chain:

```text
runtime role.FactionID
 -> faction definition
 -> faction skill/book families
```

This is especially useful for Auto Buff filtering and class-specific skill catalogs.

---

## 17. PC input binding -> semantic UI/action

`PCInputKeyBinding` contains 22 records linking PC key binding/UI-event semantics.

Use it to explain input presentation only.

Preferred automation relation remains:

```text
key/UI label
 -> actual Lua handler / semantic Game action
```

not simulated keypress as the canonical action.

---

# Join safety rules

1. **Same numeric value is not automatically a foreign key.** Require field/table semantic evidence.
2. **Static ID joins describe templates, not current existence/state.**
3. **Runtime instance ID is not template ID.**
4. **Task parameters are type-specific.** Preserve raw positional data before interpreting.
5. **NPC `ResName` is not a service contract.** Runtime dialog/shop data proves service.
6. **Packet names/IDs do not prove payload joins.** Use legitimate Lua construction.
7. **Unknown columns must be preserved** so future joins can be discovered without re-extracting the bundle.

# Highest-value joins to validate/materialize next

1. `Skills.Property -> SkillProperties` and property symbols -> `MagicAtrributes`.
2. `Skills.FactionID/BookID -> Factions/Books`.
3. `AutoSkills SkillIDs -> Skills`.
4. `Items/Equips` direct template relationship and all exact key rules.
5. TaskType-specific parameter -> NPC/Monster/Item/GrowPoint/Map joins.
6. Pet/Spirit skill/equipment/template keys.

These row-level validations will convert a large amount of static Config from “known tables” into an actual relational knowledge graph for future AI.
