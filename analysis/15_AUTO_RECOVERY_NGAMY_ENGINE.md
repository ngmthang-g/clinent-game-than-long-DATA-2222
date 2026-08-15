# Built-in recovery / Nga My support engine

Status: **VERIFIED from `AutoHp.lua`, `AutoFight_Main.lua`, `Global_Constants.lua`, `AutoHp_Layout.xml`, `Skills.xml`.**

This client already ships a fairly complete recovery/support subsystem. It is an excellent donor for an external Auto Buff implementation because it shows the game's intended semantic APIs for HP checks, teammate scanning, range checks, chase and skill use.

## Important correction: misleading internal variable name

`Global_Constants.lua` defines:

```text
C_NMBuff.PHATQUANGPHOCHIEU = 406
C_NMBuff.THANHTAMPHOTHIENCHU = 424
C_NMBuff.KIMCHAMDOKIEP = 407
C_NMBuff.CAITUHOANSINH = 408
```

However, cross-checking the actual `Skills.xml` and `AutoHp_Layout.xml` proves that the internal label `KIMCHAMDOKIEP` is **misnamed**.

Exact snapshot truth:

| Skill ID | Actual Config Name | Target/Style | Built-in AutoHp toggle |
|---:|---|---|---|
| `406` | Phật Quang Phổ Chiếu | SelfAndAlly / MultipleTargetsBuff | `PhatQuangPhoChieu` |
| `407` | **Xung Hư Dưỡng Khí** | PeacePlayer / SingleTargetBuff | internally misnamed `KimChamDoKiep` |
| `408` | Khởi Tử Hồi Sinh | PeacePlayer / SingleTargetBuff | `CaiTuHoanSinh` |
| `423` | **Kim Châm Độ Kiếp** | PeacePlayer / SingleTargetBuff | **not the built-in AutoHp 407 toggle** |
| `424` | Thanh Tâm Phổ Thiện Chú | PeacePlayer / SingleTargetBuff | `ThanhTamPhoThienChu` |

`AutoHp_Layout.xml` confirms the toggle named `TogKimChamDoKiep` visibly says:

`Sử dụng [Xung hư dưỡng khí]`.

Therefore future AI/tool code must **not** equate SkillID 407 with actual Kim Châm Độ Kiếp. The actual static Config SkillID for Kim Châm Độ Kiếp is 423.

This correction is exactly why the KB cross-checks Lua variable names against Config + visible UI text.

## Exact useful skill metadata

### 406 — Phật Quang Phổ Chiếu

- FactionID: 4 (Nga My)
- Type: Active
- Style: MultipleTargetsBuff
- TargetType: SelfAndAlly
- CastRange: 15
- AttackRadius: 7
- ProgressTime: 3000 ms
- RequireLevel: 40
- RequireWeapon: true
- IsDamageSkill: false.

### 407 — Xung Hư Dưỡng Khí

- Type: Active
- Style: SingleTargetBuff
- TargetType: PeacePlayer
- CastRange: 15
- ProgressTime: 3000 ms
- RequireLevel: 20
- RequireWeapon: false
- IsDamageSkill: false.

### 423 — Kim Châm Độ Kiếp

- Type: Active
- Style: SingleTargetBuff
- TargetType: PeacePlayer
- CastRange: 15
- ProgressTime: 0
- RequireLevel in Config row: 1
- RequireWeapon: false
- IsDamageSkill: false
- Property: `emei_jinzhendujie`.

### 424 — Thanh Tâm Phổ Thiện Chú

- Type: Active
- Style: SingleTargetBuff
- TargetType: PeacePlayer
- CastRange: 15
- ProgressTime: 1000 ms
- RequireLevel: 45
- RequireWeapon: false
- IsDamageSkill: false
- Property: `emei_qingxinputianzhou`.

### 408 — Khởi Tử Hồi Sinh

- Type: Active
- Style: SingleTargetBuff
- TargetType: PeacePlayer
- CastRange: 3
- ProgressTime: 10000 ms
- RequireLevel: 30
- RequireWeapon: false
- IsDamageSkill: false.

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
- `KimChamDoKiep` — **legacy/misleading key that actually controls 407 Xung Hư Dưỡng Khí**
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

Built-in AutoHp preference is:

1. 406 Phật Quang Phổ Chiếu if enabled and condition passes;
2. 424 Thanh Tâm Phổ Thiện Chú if enabled and condition passes;
3. **407 Xung Hư Dưỡng Khí** if the legacy `KimChamDoKiep` setting is enabled and condition passes.

Action:

`Game.RequestUsingSkillWithTarget(skillID, targetRoleID)`.

Important: the built-in AutoHp source does **not** select actual Config skill 423 Kim Châm Độ Kiếp through that toggle.

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

- check condition for ID 408;
- choose skill 408.

### Living low-HP teammate

Compute:

`Percent = floor(HP * 100 / MaxHP)`.

If below `NgaMyPercent`, call the built-in skill selector described above.

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

Therefore an external buff model can reuse the donor action logic with a read-only filtered snapshot of nearby peaceful players.

This adaptation is **not claimed as a built-in game feature**; it is a strongly grounded implementation strategy assembled from verified shipped paths.

## Which healing skill should the external tool use?

Do not blindly copy the misleading internal variable name.

If the user's configured skill is **Thanh Tâm Phổ Thiện Chú**, use semantic SkillID `424` after runtime availability/condition/cooldown checks.

If the user explicitly wants **Kim Châm Độ Kiếp**, the static Config ID is `423`; verify that the live character has/CanUse the skill before using it.

If reproducing the built-in AutoHp third fallback exactly, that fallback is **407 Xung Hư Dưỡng Khí**, despite the Lua variable being named `KIMCHAMDOKIEP`.

## Recommended prioritization policy

1. scan peaceful players;
2. apply whitelist/filter: Name / RoleID / Guild / Faction etc.;
3. compute HP%;
4. keep candidates below threshold;
5. optionally prioritize MaxHP descending;
6. select one current target;
7. choose the specifically configured semantic skill ID, checking learned/condition/cooldown state;
8. chase only if outside real cast range;
9. issue one `RequestUsingSkillWithTarget`;
10. wait for HP/buff/cast state proof;
11. rescan.

Do not queue multiple casts blindly.

## Buff maintenance unrelated to healing

`AutoFight_Main:DoAutoBuff()` handles self-buff skill lists separately:

- skip if `UTILITIES.IsAutoBuff == false`;
- iterate configured skill IDs;
- if `Game.HasBuff(skillID) == false` and `Game.CheckCondition(skillID)` passes;
- call `Game.UseSkill(skillID)`.

For richer local buff state see `analysis/17_BUFF_RUNTIME_SCHEMA.md`.

## Important implementation rule

The Lua donor demonstrates semantic actions. An external bridge still has to execute Unity/Lua/gameplay actions in a valid Unity/main-thread context. Do not translate this into arbitrary worker-thread `runtime_invoke` calls.
