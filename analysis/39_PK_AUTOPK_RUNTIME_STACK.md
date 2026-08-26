# 39 — PK / AutoPK runtime stack

Status: **VERIFIED from shipped `PKPopup.lua`, `AutoPK.lua`, `AutoFight_Main.lua`, `OtherRolePopup.lua`, `Global_Constants.lua`, TCP definitions/handler.** UI-only settings that are not consumed by the combat selector are explicitly marked.

## 1. PK modes

`C_PKMode` exact frozen values:

0 Luyện công; 1 Tổ đội; 2 Bang hội; 3 Đồ sát; 4 Thiện ác; 5 Sự kiện; 6 Liên máy chủ; 7 Liên minh; 8 Quân đoàn.

`PKPopup` sends `CMD_PKMODEL_CHANGE = 200059` with payload equal to the selected mode. The visible popup has buttons for 0,7,1,2,4,6,8,3; mode 5 exists in the enum but no matching popup button was found in this layout/source.

## 2. AutoPK engine

`C_AutoModel.PK = 2`.

The same `AutoFight_Main` state machine starts PK mode and performs target/skill/chase/cast behavior. The target resolver ultimately uses:

`Game.GetNearByEnemies(false, true, -1)`

and selects the first returned enemy when there is no valid locked/trigger target.

### Important incomplete UI/config behavior

`AutoPK.lua` exposes and saves:

- `AutoPkAgian`
- `IsLowHpTarget`
- `IsFactionTarget`
- `FactionID`
- `SkillPK`
- `UsingCombo`.

However, the shipped `FindAutoPKTarget()` does **not** consume `IsLowHpTarget`, `IsFactionTarget`, or `FactionID`; it uses the nearby-enemy list order. Treat those three as UI/config intent, not verified target-priority behavior.

## 3. Retaliation trigger

`CMD_PK_NOTIFY = 200078` supplies an attacker RoleID to `PkTriger(attackerRoleID)`.

If `AutoPkAgian=true` and current auto mode is Train, the engine removes the train flag, stores the trigger target and enters AutoPK. Trigger targeting is time-bounded (20-second lifecycle in shipped code) and invalidated when distance/death/return conditions fail.

This is a concrete bridge between Train and defensive AutoPK.

## 4. Skill selection

AutoPK uses configured PK skills, validates usable skill data and target semantics, then casts through semantic APIs (`RequestUsingSkillWithTarget` / positional form) after range/chase checks.

A cross-feature coupling exists:

`PickSkillReady(SkillPkList, AUTOPK.UsingCombo, AUTOTRAIN.UsingF1Key)`.

So PK currently reuses Train's `UsingF1Key` setting. A standalone tool implementation should either preserve this compatibility deliberately or separate it explicitly instead of accidentally changing behavior.

The visible AutoPK layout contains 14 skill slots. Source constant `MAX_PK_SKILLS=14`; default serialized skill string contains 15 `-1` values and some comments claim another count. Use actual UI/runtime handling, not stale comments.

## 5. Related direct player actions

Selected-player popup uses `CMD_OTHER_ROLE_COMMAND = 200051`.

Relevant commands:

- `C_OtherRoleCommand.PKChallenger = 4`
- `Trade = 7`
- `Proclaim = 8`.

Force/proclaim PK request: `8:targetRoleID`.

Challenge is separate: `CMD_CHALLENGE = 200075`, payload `C_ChallengeAction.Request:RoleID:useRandomArdorBuff` where the last value is 0/1.

## 6. Tool contract

A robust PK controller should resolve current legal enemy state, revalidate target RoleID/death/distance/map generation, select/chase/cast one action at a time, and use fresh target/cooldown/HP/death state as proof. UI toggles that are not consumed by shipped selection logic must not be presented as already-working semantics.
