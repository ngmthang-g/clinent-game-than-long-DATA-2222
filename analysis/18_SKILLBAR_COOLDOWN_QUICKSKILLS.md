# SkillBar / cooldown / quick-skill semantics

Status: **VERIFIED from decrypted `SkillBar.lua`, `SkillTooltip.lua`, `SetFightSkill_QuickSkillsTab.lua`, `TCPPacketDefine.lua`.**

This resolves several old automation assumptions around F1/quick-skill buttons. The shipped UI exposes semantic SkillID state and cooldown data directly.

## Quick-skill source of truth

The stock SkillBar reads:

`Game.RoleData.QuickSkills`

Serialized format is a semicolon-separated mapping:

`position_skillID;position_skillID;...`

Each entry is split by `_` into:

- `Position`
- `SkillID`.

The SkillBar stores this in `QuickSkillsData[position] = skillID`.

## Five quick-skill pages

The UI supports five tabs/sites.

For page index `idx = 1..5`:

`site = idx - 1`

and:

`sitePosition = 100 * site`.

Within each site:

- offset `0` = MainSkillButton
- offsets `1..9` = SkillButton_1..9.

Thus page positions are grouped approximately as:

- page 1: 0..9
- page 2: 100..109
- page 3: 200..209
- page 4: 300..309
- page 5: 400..409.

Do not treat F1/visible button coordinates as the real skill identity; the real identity is the mapped SkillID.

## Exact skill action from the SkillBar

`SkillBar:ButtonSkillHovered(uiButton)` obtains:

`skillID = uiButton.Tag`

and invokes:

`Game.UseSkill(skillID)`.

The layout binds skill buttons through hover-as-click/hover-tick behavior, but the semantic gameplay action is simply `Game.UseSkill(skillID)`.

Therefore an internal auto does not need to press F1 physically if it already knows the desired SkillID and the correct semantic action path is valid for that skill.

## Cooldown source of truth

For every visible skill, the stock UI calls:

`Game.GetSkillCooldown(skillID)`.

Returned data is indexed as:

- `[1] = passedTicks`
- `[2] = cooldownTicks`.

The UI considers the skill ready when:

- `cooldownTicks <= 0`, or
- `passedTicks >= cooldownTicks`.

Otherwise remaining time is:

`cooldownTicks - passedTicks`

and the visible seconds are:

`floor((cooldownTicks - passedTicks) / 1000)`.

The radial fill is:

`1 - passedTicks / cooldownTicks`.

### Tool implication

A cooldown-aware action engine can read semantic cooldown state instead of sleeping an assumed cooldown duration.

Useful normalized fields:

```text
SkillID
PassedTicks
CooldownTicks
RemainingTicks = max(0, CooldownTicks-PassedTicks)
Ready = CooldownTicks<=0 OR PassedTicks>=CooldownTicks
```

## `Game.HasSkill(skillID)` guard

Before rendering/cooldown logic, the stock UI checks:

`Game.HasSkill(skillID)`.

If false it treats the slot as empty (`-1`).

An external auto should similarly reject an unlearned/unavailable SkillID before attempting a cast.

## Skill template/runtime metadata

`SkillTooltip` calls:

`Game.GetSkillTemplateData(skillID)`

and directly consumes:

- `Name`
- `Icon`
- `RequireLevel`
- `RequireWeapon`
- `ShortDescription`
- `CastRange`
- `AttackRadius`
- `ProgressTime`
- `Style`
- `Description`.

It then calls:

- `Game.GetSkillProperties(skillID, level)`
- `Game.GetSkillEnchantProperties(skillID)`.

This makes the client capable of semantic checks/description far beyond keyboard-slot assumptions.

## Progress/channel semantics

If `ProgressTime > 0`, the tooltip distinguishes:

- regular cast/channel time;
- `RangedSingleTargetChaining`;
- `MultipleTargetsAroundSelfChaining`.

For chaining styles, ProgressTime is described as the interval between continuous casts; otherwise it is displayed as cast/channel time.

This matters when building timeouts: a skill may legitimately remain in a progress state and should not immediately be treated as stuck.

## Saving quick-skill configuration

`SetFightSkill_QuickSkillsTab:ButtonSaveSettingClicked()` builds a list of objects:

```text
{ Position = position, SkillID = skillID }
```

and sends:

`CMD_SAVE_QUICK_SKILLS = 100009`.

It also updates `Game.RoleData.QuickSkills` locally and calls `SkillBar:UpdateQuickSkillsData()`.

### Selection guards in the stock UI

When choosing a skill for a quick slot, the UI rejects:

- missing book/type data;
- passive skills (`type == "Passive"`);
- skills whose book level is below `Game.GetSkillRequire(skillID)`;
- non-book skills when local role level is below required level.

## Auto Train / Auto Buff relevance

A robust skill-action decision can combine:

1. `Game.HasSkill(skillID)`;
2. `Game.CheckCondition(skillID)` where the donor code uses it;
3. `Game.GetSkillCooldown(skillID)` ready state;
4. `Game.GetSkillLuaData/GetSkillTemplateData` cast range / style;
5. target eligibility/range;
6. one semantic `Game.UseSkill` or `RequestUsingSkillWithTarget` action;
7. state proof.

This is more precise than repeated F1 key simulation.

## Pet and Spirit skill state

The same SkillBar also obtains:

- `Game.GetCurrentPetActiveSkills()`
- `Game.GetCurrentSpiritActiveSkills()`

and applies the same `SetSkillIcon` + `GetSkillCooldown` logic.

So pet/spirit active skills are also represented by semantic SkillIDs and cooldown state.

## What future AI should not repeat

- do not identify a skill solely as “F1/F2/F3”;
- do not assume cooldown from visual animation;
- do not sleep for a hardcoded skill delay when `GetSkillCooldown` is available;
- do not attempt passive/unlearned skills;
- do not rewrite quick-skill settings just to cast a known SkillID unless the actual user feature specifically requires changing the game UI configuration.
