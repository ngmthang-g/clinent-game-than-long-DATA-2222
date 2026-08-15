# Pet / Spirit runtime and built-in automation

Status: **VERIFIED from decrypted `AutoPet.lua`, `AutoFight_Main.lua`, `MainUI_PetHeader.lua`, `MainUI_SpiritHeader.lua`, `PetAttackMode.lua`, `Global_Constants.lua`, `TCPPacketDefine.lua`.**

The client already exposes structured pet/spirit state, semantic summon actions, active skill lists and a configurable pet behavior model.

## Current pet runtime object

`Game.CurrentPet` is used continuously by the stock MainUI.

Fields directly consumed:

- `RoleID`
- `HPPercent`
- `Avarta`
- `Name`
- `Level`.

Pet target buffs are rendered using:

`Game.GetTargetBuffIcons(pet.RoleID)`.

A `RoleID == -1` or HPPercent <= 0 causes the pet header to hide.

## Current Spirit runtime object

`Game.CurrentSpirit` is consumed with:

- `RoleID`
- `Avarta`
- `EnergyPercent`
- `Level`.

If nil or RoleID == -1, the Spirit UI hides.

## Pet list/config APIs

Auto configuration uses:

- `Game.GetCurrentPetList()`
- `Game.GetPetInfo(dbPetID)`
- `Game.GetPetAvatar(ResID)`.

Spirit selection uses:

- `Game.GetCurrentSpiritList()`
- each record's `DbID`, `Name`.

## Exact Pet action constants

`C_PetAction`:

| Action | Value |
|---|---:|
| Undefined | 0 |
| Release | 1 |
| CallFight | 2 |
| CallBack | 3 |
| ChangeName | 4 |
| AssignRemainPoint | 5 |
| FeedFood | 6 |
| GiveToy | 7 |
| DestroyPet | 100 |

Packet:

`CMD_PET_ACTION = 200050`.

Built-in summon payload:

`C_PetAction.CallFight:PetDbID`

or numerically:

`2:PetDbID`.

## Exact Spirit actions

`C_SpiritAction`:

- Undefined = 0
- Release = 1
- CallFight = 2
- CallBack = 3
- ChangeName = 4
- Charge = 6.

Packet:

`CMD_SPIRIT_ACTION = 200149`.

Built-in summon payload:

`2:SpiritDbID`.

## Built-in Auto Pet summon logic

`AutoFight_Main:DoAutoPet()`:

- if current pet is absent;
- reject while `Game.IsProgress()`;
- require `IsAutoCallPet == true`;
- throttle call attempts to >5000 ms;
- use selected `PetIDSelect`, or first available pet when `-1`;
- optionally refuse summon when selected pet has reached configured callback level;
- send `CMD_PET_ACTION` CallFight.

This is a stable semantic donor for pet resummon behavior.

## Pet skill automation

When a pet is present, the built-in engine processes pet-related support about once per second.

### Dedication

If enabled and local player HPPercent is below threshold:

1. `Game.GetDedicationSkill()`
2. ensure skill != -1
3. `Game.CheckCondition(skillID)`
4. `Game.UseSkill(skillID)`.

### Blood Sacrifice

If enabled and local player MPPercent is below threshold:

1. `Game.GetBloodSacrificeSkill()`
2. condition check
3. `Game.UseSkill(skillID)`.

### Pet active skills

If `AutoSkillPet == true`:

- `Game.GetCurrentPetActiveSkills()` returns SkillIDs;
- engine checks each with `Game.CheckCondition`;
- calls `Game.UseSkill(SkillID)`.

The built-in source excludes SkillIDs 696, 697, 686 and 687 from this generic loop.

These exclusions are VERIFIED source behavior; their exact semantic reason should not be invented without inspecting those skill templates.

## Spirit auto summon

`AutoFight_Main:DoAutoSprit()`:

- if current Spirit is already active -> no action;
- wait if `Game.IsProgress()`;
- require `IsAutoCallSprit`;
- throttle >5000 ms;
- require selected `SpritIDSelect` != -1;
- send `CMD_SPIRIT_ACTION` CallFight.

The spelling `Sprit` is a legacy source typo; semantic meaning is Spirit/Phụ thân.

## Pet attack behavior modes

`PetAttackMode.lua` exposes exact modes:

| Mode | Meaning |
|---:|---|
| 0 | Chỉ đi theo |
| 1 | Đánh tự do |
| 2 | Đánh theo chủ |
| 3 | Chỉ Buff |
| 4 | Lùa quái |

The popup does not directly send a packet. It finds:

`GUI.FindUI("AutoFight_Main")`

and calls:

`AutoFight_Main:SetPetAttackModel(mode)`.

That function updates `AutoFightSettings["PET"]["AttackModel"]` and persists settings.

### Consequence

Pet attack mode is a built-in Auto engine configuration, not merely a temporary UI label.

## AutoPet settings schema

The stock settings surface includes:

- IsAutoCallPet
- PetIDSelect
- BloodSacrifice
- BloodSacrificeValue
- Dedication
- DedicationValue
- AutoSkillPet
- AutoCallBackPet
- CallBackPetNumber
- AutoEat
- HpPercent
- AutoInjoy
- InjoyValue
- AttackModel
- IsAutoCallSprit
- SpritIDSelect.

This matches the PET serialization documented in `database/AUTO_SETTINGS_SCHEMA.md`.

## Pet/Spirit skill cooldown

The stock SkillBar also obtains:

- `Game.GetCurrentPetActiveSkills()`
- `Game.GetCurrentSpiritActiveSkills()`

and uses the same `Game.GetSkillCooldown(skillID)` UI path used for role skills.

So pet/spirit active skills also have semantic SkillIDs + cooldown state available to the client.

## Useful state machine for pet resummon

```text
read CurrentPet
 -> if active/alive: no summon
 -> if local Progress/Loading/Death/Captcha: wait
 -> select configured Pet DBID
 -> validate PetInfo + callback-level policy
 -> send one CMD_PET_ACTION 2:PetDbID
 -> wait CurrentPet.RoleID != -1 / pet event
 -> continue
```

Do not resend summon every frame.

## Task/Quest integration

The built-in Auto Quest uses the same `CMD_PET_ACTION CallFight` path to satisfy `C_TaskType.CallFightPet` objectives, then reloads task progress.

This demonstrates that pet actions are composable semantic actions used by multiple systems.

## Multi-client rule

Pet/Spirit DB IDs, current RoleIDs and Auto settings are per-character/per-process state. Never share a live Pet/Spirit object or pointer between clients.

## Safety

Destructive actions such as Release/DestroyPet are documented for completeness but should never be part of generic Auto Train/Auto Pet behavior without an explicit user feature and confirmation policy.
