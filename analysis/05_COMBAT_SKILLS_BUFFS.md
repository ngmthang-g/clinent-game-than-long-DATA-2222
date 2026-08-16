# Combat / Skills / Buffs / Auto Fight — current semantic model

> Phase 2/3 solved the old uncertainties around skill config, buff runtime schema and built-in Auto Fight. This document now separates verified combat semantics from the smaller set of remaining runtime questions.

---

## 1. Core conclusion

Combat is not a black box and should not be automated as keyboard/mouse macros.

The frozen client exposes:

- structured nearby target data;
- semantic target/chase/movement APIs;
- semantic skill APIs;
- skill cooldown state;
- structured local buff state;
- static Skills/SkillProperties/AutoSkills/MagicAttributes tables;
- readable built-in AutoFight Lua;
- combat event/packet vocabulary.

The preferred architecture is:

```text
runtime snapshot
 -> target/skill policy
 -> one semantic action
 -> state/event proof
 -> fresh snapshot
```

---

## 2. Skill/runtime API — VERIFIED existence and shipped use

High-value members include:

- `GetAbilities`
- `GetAbilityLevel`
- `GetAbilityTemplateData`
- `GetAbilityName`
- `GetAbilityDescription`
- `GetAbilityIcon`
- `UseSkill(skillID)`
- `RequestUsingSkill`
- `RequestUsingSkillWithPos`
- `RequestUsingSkillWithTarget`
- `GetSkillLuaData`
- `IsSkillRequireTarget`
- `CanUseSkill`
- `GetSkillCooldown(skillID)`.

Shipped SkillBar uses:

`Game.UseSkill(skillID)`.

This proves that a physical F1/F2 key is only a UI/input mapping, not semantic skill identity.

---

## 3. Cooldown — VERIFIED semantic state

`Game.GetSkillCooldown(skillID)` returns:

- `passedTicks`
- `cooldownTicks`.

Ready condition used by analysis:

```text
cooldownTicks <= 0
OR
passedTicks >= cooldownTicks
```

This enables exact readiness policy rather than fixed per-skill sleeps.

QuickSkills are also structured (`position_skillID` mappings), so the tool can distinguish UI slot from actual SkillID.

Canonical detail:

`analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`.

---

## 4. Target / chase / range layer

High-value semantic APIs:

- `SelectTarget`
- `ClickToObject`
- `ChaseTarget`
- `get_CurrentChaseTargetID`
- `IsSelectTargetDie`
- `IsAllowDeadTarget`
- `GetDistance`
- `HasPath`
- `CanMove`.

Shipped nearby-player/enemy UIs already expose structured RoleID/HP/MaxHP and use RoleID for targeting.

A target policy can therefore operate as:

```text
query nearby actors
 -> filter by semantic type/relationship/alive state
 -> score by policy
 -> SelectTarget / ChaseTarget
 -> use actual SkillID
 -> observe cooldown/HP/death/buff/progress state
```

No image recognition is required for ordinary targets already present in AOI.

---

## 5. Static `Skills.xml` — VERIFIED, 2,091 rows

Normalized fields already recovered/documented include:

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

This means support/damage/target-type candidate discovery can be done offline before touching runtime.

Static row meaning is not current ownership/readiness; those remain runtime questions.

---

## 6. `SkillProperties.xml` — VERIFIED, 2,044 rows

The old statement “detailed skill/buff config is only probable” is obsolete.

A dedicated table exists for skill property definitions.

High-value join:

```text
Skills.ID
 -> Skills.Property
 -> SkillProperties
 -> MagicAtrributes symbols/descriptions
```

This is one of the highest-value still-under-normalized datasets because it can explain skill effect semantics beyond display description.

Extraction/index priorities are documented in:

`analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

---

## 7. `AutoSkills.xml` — VERIFIED, 300 rows

Catalog evidence shows activation type/value/cooldown/SkillID semantics.

Potential use:

- recover shipped automatic-skill trigger policies;
- identify state/threshold/timing-driven automatic skills;
- understand internal auto behavior without mimicking visible UI clicks.

Numeric activation modes should not be renamed into guessed human meanings until cross-checked with Lua/config usage.

---

## 8. `MagicAtrributes.xml` — VERIFIED, 509 rows

The client contains a semantic dictionary of `magic_*` effect symbols.

Examples observed include concepts for:

- max HP;
- cooldown modification/reset;
- stack limits;
- buff removal on timeout/move/action;
- invisibility/see-invisibility;
- unable-to-use-skill;
- drag/blink/swap position;
- revive/death effects;
- hit/crit behavior;
- traps/puppets;
- autoskill/called-skill behavior.

The important change from the old phase is that these are no longer merely free-floating metadata strings: `MagicAtrributes.xml` is a **verified 509-row static semantic table**.

Do not assume every symbol is used by every skill/buff; join through actual SkillProperties/equipment/buff data.

---

## 9. Buff runtime schema — VERIFIED

High-value APIs:

- `GetBuffs`
- `GetBuffProperties`
- `HasBuff`
- `GetBuffData`
- `GetTargetBuffIcons`
- `SendRemoveBuff`.

`Game.GetBuffs()` records expose:

- `BuffID`
- `DurationTick` in milliseconds
- `Stack`.

`Game.GetBuffData(BuffID)` exposes at least level/stack-related data.

`Game.GetBuffProperties(BuffID)` exposes semantic magic properties.

Add/Update/Remove buff events drive shipped UI updates.

Therefore exact local buff-aware automation can use actual BuffID/duration/stack rather than only HP thresholds.

Still targeted if needed:

- source/owner field;
- richer target buff IDs/durations beyond current target icon path;
- any specific positive/negative categorization not already obtainable from static/property data.

Canonical detail:

`analysis/17_BUFF_RUNTIME_SCHEMA.md`.

---

## 10. Built-in Auto Fight — VERIFIED semantic engine

Readable `AutoFight_Main` Lua proves the game has a real internal auto engine.

`C_AutoModel`:

- None = 0
- Train = 1
- PK = 2
- Quest = 3
- AutoPath = 4
- Fllow = 5
- FuBen = 6.

Train start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

Stop:

`StartAutoFight(C_AutoModel.None)`.

The visible `Đánh quái` tab is **settings**, not the start action.

Shipped engine uses semantic world/target/skill/path APIs such as nearby sprite queries, `HasPath`, `SelectTarget`, `ChaseTarget`, target/position skill requests and target-death checks.

Old PROBABLE architecture around “maybe there is an internal AutoFight loop” is now fully resolved.

Canonical detail:

`analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`.

---

## 11. Auto Train settings / radius / lure

`AutoTrainMonster_Layout` and Lua expose actual settings for:

- monster whitelist;
- scan/radius behavior;
- lure mode;
- attack-in-radius;
- skill slots;
- combo/basic-skill toggles.

A few deeper internal center/return/ranger state fields may still be worth targeted mapping if a feature needs to duplicate exact stock behavior, but there is no reason to rediscover whether radius/monster policy exists.

Remaining hypothesis is narrowed in `research/HYPOTHESES.md`.

---

## 12. Nga My support skill truth — VERIFIED correction

Frozen `Skills.xml`:

- 406 = Phật Quang Phổ Chiếu
- **407 = Xung Hư Dưỡng Khí**
- 408 = Khởi Tử Hồi Sinh
- **423 = Kim Châm Độ Kiếp**
- 424 = Thanh Tâm Phổ Thiện Chú.

Legacy Lua variable `KIMCHAMDOKIEP` misleadingly points to 407. Do not copy that name/value association into new code or data.

Built-in AutoHp fallback observed:

`406 -> 424 -> 407`.

Canonical truth table:

`database/NGAMY_SUPPORT_SKILLS.md`.

---

## 13. Team-heal donor — VERIFIED exact flow

Built-in Nga My support logic reads teammate state including death/HP/MaxHP/Position/RoleID, checks skill/range state, chases if needed and calls target-skill semantics.

This gives a reliable donor for:

- HP threshold selection;
- range handling;
- semantic chase;
- target skill request;
- state proof.

It does **not** automatically prove the server accepts every beneficial skill on every non-team peaceful player.

That remains a targeted runtime acceptance question.

---

## 14. Auto Buff should combine vitals and buff state

A robust policy can use two independent signals:

1. **need state** — HP/MaxHP/priority/filter;
2. **effect state** — BuffID/duration/stack/presence.

Example policy:

```text
snapshot eligible nearby peaceful players
 -> filter whitelist/guild/faction/level/MaxHP/etc.
 -> rank by configured policy
 -> revalidate target
 -> check desired buff/cooldown/range/progress
 -> one semantic cast
 -> wait cooldown/buff/HP/state proof
 -> fresh snapshot
```

Do not spam a buff merely because HP is low if the desired effect is already active and non-refreshable.

---

## 15. Combat network/event vocabulary

Verified names include:

- `CMD_USE_SKILL`
- `CMD_NEW_MISSILE`
- `CMD_NEW_SKILL_EXPLODE`
- `CMD_SKILL_DAMAGE`
- `CMD_SKILL_HEAL`
- `CMD_OBJECT_DEATH`
- `CMD_ADD_BUFF`
- `CMD_UPDATE_BUFF`
- `CMD_REMOVE_BUFF`
- movement/drag/trap/puppet/PK-related commands.

Exact packet constants are available where defined in `TCPPacketDefine`.

For action execution, semantic `Game` API is preferred.

For analytics, inbound damage/heal/death/buff events are a promising observation source.

Do not infer request direction/payload from a command name alone.

---

## 16. Combat recorder — still PROBABLE, but well grounded

Structured event vocabulary strongly suggests a recorder can capture some combination of:

- attacker/target identity;
- SkillID;
- damage/heal values;
- death timing;
- buff lifecycle;
- target/spot efficiency.

Still needs targeted handler/payload mapping for:

- exact event fields;
- crit/block/elemental flags;
- XP/loot linkage.

Track this as a telemetry research target, not a solved full schema.

---

## 17. Main-thread/state requirement

Skill, target, Lua/UI and other mutable game actions should execute through the validated game-owned action path, not arbitrary external worker-thread invocation.

Canonical action pattern:

```text
read-only Observer
 -> policy decision
 -> max one mutable action
 -> MainThread.Execute(Action)
 -> semantic Game/Lua action
 -> concrete runtime/server proof
 -> next decision
```

The `MainThread.Execute -> queue -> Update -> Action.Invoke` consumer chain itself is already VERIFIED.

---

## 18. Remaining high-value combat data work

The best next **knowledge** work is not more broad GameAssembly reverse. It is normalization/indexing of:

1. `Skills` 2,091 rows;
2. `SkillProperties` 2,044 rows;
3. `AutoSkills` 300 rows;
4. `Factions` 17 rows;
5. `Books` 128 rows;
6. `MagicAtrributes` 509 rows.

Goal:

```text
SkillID
 -> exact name/faction/type/target/range/cooldown/property
 -> property effects
 -> magic-symbol meanings
 -> current runtime ownership/cooldown/buff state
```

This will let future AI answer most skill/support/combat questions by lookup rather than reverse analysis.

---

## 19. Remaining targeted runtime questions

Only investigate when a feature needs them:

- server acceptance rules for specific beneficial skills on non-team players;
- richer target-buff data beyond icons/current known local schema;
- additional actor combat fields not already consumed by shipped UI;
- exact combat-event payload schema for a recorder;
- any internal AutoFight center/return state needed beyond documented Lua settings.

Do not re-question the existence of Skills/SkillProperties/AutoFight/buff duration/skill cooldown: those are already VERIFIED.
