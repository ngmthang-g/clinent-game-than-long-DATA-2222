# Built-in recovery / Nga My support engine

Status: **VERIFIED from `AutoHp.lua`, `AutoFight_Main.lua`, `Global_Constants.lua`.**

This client already ships a fairly complete recovery/support subsystem. It is an excellent donor for an external Auto Buff implementation because it shows the game's intended semantic APIs for HP checks, teammate scanning, range checks, chase and skill use.

## Exact Nga My skill constants

From `Global_Constants.lua`:

| Constant | Skill ID | Meaning |
|---|---:|---|
| `C_NMBuff.PHATQUANGPHOCHIEU` | `406` | Phật Quang Phổ Chiếu |
| `C_NMBuff.THANHTAMPHOTHIENCHU` | `424` | Thanh Tâm Phổ Thiện Chú |
| `C_NMBuff.KIMCHAMDOKIEP` | `407` | Kim Châm Độ Kiếp |
| `C_NMBuff.CAITUHOANSINH` | `408` | Cải Tử Hoàn Sinh |

These IDs are source constants in the frozen client, not guessed offsets.

## AutoHp settings exposed by shipped UI

`AutoHp:GetSettings()` writes:

- `AutoRegenHP`
- `AutoRegenHPPercent`
- `AutoRegenMP`
- `AutoRegenMPPercent`
- `AutoComeback`
- `AutoRevival`
- `IsNgaMy`
- `NgaMyPercent`
- `PhatQuangPhoChieu`
- `ThanhTamPhoThienChu`
- `KimChamDoKiep`
- `CaiTuHoanSinh`
- selected HP/MP medicine template IDs.

The UI selects HP medicine by `Game.IsHPMedicine(ItemID)` and MP medicine by `Game.IsMPMedicine(ItemID)`.

## Built-in local HP/MP recovery

`AutoFight_Main:DoAutoRegen()` checks `Game.IsProgress()` first.

When the configured threshold is crossed it finds the configured item in the bag and uses the normal item action packet path.

The function throttles recovery processing to roughly one pass per second via `LastTrigerHpRegen`.

## Built-in Nga My self-heal

If:

- `Game.RoleData.FactionID == 4`;
- `IsNgaMy == true`;
- MP is sufficient;
- self HP% is below `NgaMyPercent`;

then `TryUseNgaMySkill(config, -1)` is called.

Skill preference is:

1. Phật Quang Phổ Chiếu if enabled and `Game.CheckCondition(406)` passes;
2. Thanh Tâm Phổ Thiện Chú if enabled and `Game.CheckCondition(424)` passes;
3. Kim Châm Độ Kiếp if enabled and `Game.CheckCondition(407)` passes.

Action:

`Game.RequestUsingSkillWithTarget(skillID, targetRoleID)`.

## Built-in teammate healing/revive donor logic

When the character is in a team, the engine calls:

`Game.GetNearTeammates(self:GetCurrentPosition(), true)`.

For every teammate it reads at least:

- `IsDeath`
- `HP`
- `MaxHP`
- `Position`
- `RoleID`.

### Dead teammate

If the teammate is dead and `CaiTuHoanSinh` is enabled:

- check `Game.CheckCondition(C_NMBuff.CAITUHOANSINH)`;
- choose skill `408`.

### Living low-HP teammate

Compute:

`Percent = floor(HP * 100 / MaxHP)`.

If below `NgaMyPercent`, call `GetBestNgaMySkill(config)`.

### Range handling

For the selected skill:

1. `SkillData = Game.GetSkillLuaData(SkillUsing)`;
2. `distanceToTarget = Game.GetDistance(TeamMember.Position, selfPosition)`;
3. `skillCastRange = Game.CellToDistance(SkillData.CastRange)`;
4. enforce minimum range of `Game.CellToDistance(2)`;
5. if outside range, call `Game.ChaseTarget(RoleID, skillCastRange - 40, successCallback, failCallback, true)`;
6. success callback calls `Game.RequestUsingSkillWithTarget(SkillUsing, RoleID)`;
7. if already in range, call `RequestUsingSkillWithTarget` immediately.

This is a very valuable **known-good donor pattern** for support automation.

## Generalizing to nearby peaceful players

The stock support loop is team-based, but `MainUI_NearByPlayers_PlayersTab.lua` independently proves that `Game.GetNearByPeacePlayers(limit)` returns structured friendly-player records containing at least RoleID, HP, MaxHP, Name, Level, FactionID, GuildName and TeamRank.

Therefore the desired external buff model can reuse the donor action logic while replacing the source list:

`GetNearTeammates(...)`

with a read-only filtered snapshot derived from:

`Game.GetNearByPeacePlayers(limit)`.

This adaptation is **not claimed as a built-in game feature**; it is a strongly grounded implementation strategy assembled from two verified shipped code paths.

## Recommended prioritization policy for the user's buff design

A stable policy can be:

1. scan peaceful players;
2. apply user whitelist/filter: Name / RoleID / Guild / Faction etc.;
3. compute `HPPercent = HP * 100 / MaxHP`;
4. keep only candidates below configured threshold;
5. optionally prioritize `MaxHP` descending;
6. select one target;
7. choose best enabled Nga My skill whose `CheckCondition` passes;
8. chase only if outside real skill cast range;
9. issue one `RequestUsingSkillWithTarget`;
10. wait for HP/buff/cast state proof before choosing the next target.

Do not queue multiple casts blindly.

## Buff maintenance unrelated to healing

`AutoFight_Main:DoAutoBuff()` handles self-buff skill lists separately:

- skip if `UTILITIES.IsAutoBuff == false`;
- iterate configured skill IDs;
- if `Game.HasBuff(skillID) == false` and `Game.CheckCondition(skillID)` passes;
- call `Game.UseSkill(skillID)`.

This proves the game already uses buff presence + skill-condition semantics instead of UI/pixel inference.

## Death handling integration

Recovery settings also include:

- `AutoRevival`
- `AutoComeback`.

The Auto engine stores death map/position, sends normal revive, then can navigate back using `Game.GoTo`.

This means healing/buff logic should pause when `Game.RoleData.IsDeath` or the Revival lifecycle is active, and resume only after spawn/state proof.

## Important implementation rule

The Lua donor demonstrates the **semantic actions**. An external bridge still has to execute Unity/Lua/gameplay actions in a valid Unity/main-thread context. Do not translate this into arbitrary worker-thread `runtime_invoke` calls.
