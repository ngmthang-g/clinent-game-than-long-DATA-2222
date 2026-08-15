# Built-in AutoSettings schema

Status: **VERIFIED from `AutoFight_Main.lua` and Auto settings tab Lua.**

The client persists built-in auto configuration in `Game.RoleData.AutoSettings` and also sends it to the server/shared-parameter system.

## Version

`AUTOVERSION_DEFINE = "4.1"`

If loaded data has another version, `AutoFight_Main:LoadAutoConfig()` resets defaults and saves them again.

## Persistence packet

Packet:

`G_TCPPacketDefine.CMD_SHARED_PARAMETER = 200024`

Save payload construction:

`C_SharedParameterType.Set : "AutoSettings" : AUTOSETINGDATA`

The Lua code builds it with:

`String.Format("{0}:{1}:{2}", C_SharedParameterType.Set, "AutoSettings", AUTOSETINGDATA)`.

It then also assigns:

`Game.RoleData.AutoSettings = AUTOSETINGDATA`.

## Top-level serialized structure

Segments are separated by `#`:

```text
version#AUTOTRAIN#PICKITEM#UTILITIES#REGENE#PET#AUTOPK#FUBEN
```

Fields inside each segment are separated by `|`.

## AUTOTRAIN

Order:

1. `IsAttackMonsterInList` bool
2. `AttackMonsterList` string
3. `IsLureModel` bool
4. `IsTrainInRanger` bool
5. `RangerScan` number
6. `AutoTrainSkillList` string
7. `UsingCombo` bool
8. `UsingF1Key` bool
9. `GiveUpMonsterOutRanger` bool

Defaults:

- false
- empty list
- lure false
- train-in-radius true
- radius 500
- 7 skill slots = `-1_-1_-1_-1_-1_-1_-1`
- combo false
- F1/basic true
- give-up-outside-radius false.

## PICKITEM

Order saved by `SaveSetting()`:

1. `IsOn`
2. `PickRanger`
3. `IsFilterItem`
4. `FilterItemSettings`
5. `AutoEatX2`
6. `AutoUsingItem`
7. `UsingItemList`
8. `IsAutoDropItem`
9. `DropItemSettings`

Defaults:

- off
- radius 500
- filter off
- `FilterItemSettings = "0_1_3_0_1"`
- AutoEatX2 false
- AutoUsingItem false
- empty UsingItemList
- auto-drop false
- empty DropItemSettings.

### Apparent source bug / mismatch

`LoadAutoConfig()` assigns:

`PickItem["DropItemSettings"] = PickItemPrams[8]`

but saved field 8 is `IsAutoDropItem`; the string settings are field 9.

This is a **verified source-code mismatch**. Runtime consequence has not been separately tested. Future tool code should not copy this indexing mistake.

## UTILITIES

Order:

1. `AutoAcceptInviteTeam`
2. `AutoRejectInviteTeam`
3. `AutoRejectTrade`
4. `AutoLevelUp`
5. `LevelUpSet`
6. `IsAutoBuff`
7. `AutoBuffSkillList`
8. `ChatSelect`
9. `ChatCostumeChannel`
10. `ChatSelectSend`
11. `AutoRejectEmoji`
12. `AutoRejectMount`
13. `RejectJoinGuild`
14. `RejectJoinAllies`

Default buff list contains 20 `-1` slots.

## REGENE

Order:

1. `AutoRegenHP`
2. `AutoRegenHPPercent`
3. `AutoRegenMP`
4. `AutoRegenMPPercent`
5. `AutoComeback`
6. `AutoRevival`
7. `HPItemRegen`
8. `MPItemRegen`
9. `IsNgaMy`
10. `NgaMyPercent`
11. `PhatQuangPhoChieu`
12. `ThanhTamPhoThienChu`
13. `KimChamDoKiep`
14. `CaiTuHoanSinh`

Defaults:

- thresholds 50%;
- selected medicine IDs `-1`;
- all automatic options false.

Exact Nga My IDs are documented in `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`.

## PET

Order:

1. `IsAutoCallPet`
2. `PetIDSelect`
3. `BloodSacrifice`
4. `BloodSacrificeValue`
5. `Dedication`
6. `DedicationValue`
7. `AutoSkillPet`
8. `AutoCallBackPet`
9. `CallBackPetNumber`
10. `AutoEat`
11. `HpPercent`
12. `AutoInjoy`
13. `InjoyValue`
14. `AttackModel`
15. `IsAutoCallSprit`
16. `SpritIDSelect`.

## AUTOPK

Order:

1. `AutoPkAgian`
2. `IsLowHpTarget`
3. `IsFactionTarget`
4. `FactionID`
5. `SkillPK`
6. `UsingCombo`.

## FUBEN

Base fields:

1. `SelectedFuBen`
2. `AutoRepeat`
3. `RepeatCount`
4. `FollowLeader`
5. `AcceptFuBenInvite`
6. `AutoInviteMembers`
7. `AutoRevive`
8. `DesiredMembers`
9. `MinInviteLevel`
10. `ScheduleEnabled`.

Then eight schedule records are serialized, each as:

`Enabled | Hour | Minute | FuBen`.

### Scheduler implementation mismatch

The settings schema supports 8 schedule entries, but the inspected `MainUI_BackgroundWork:DoFuBenSchedulerTick()` source explicitly checks only Schedule 1, 2 and 3.

This is another source-level mismatch worth remembering if a user reports schedule 4–8 not firing.

## Boolean representation

The auto service serializes bools as integer `0/1` through `BoolToInt` and converts them back using `IntToBool`.

## Design use

Future AI should use this document to understand built-in Auto configuration and persistence. It does **not** imply an external tool must overwrite `Game.RoleData.AutoSettings`; a separate tool-owned settings model may be safer. The schema is especially useful for reading/importing existing game Auto preferences or reusing donor defaults.
