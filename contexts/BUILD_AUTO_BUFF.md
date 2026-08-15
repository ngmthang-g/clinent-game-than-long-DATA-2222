# Context Pack — Build Auto Buff

## Scope

Use for Nga My support/healing of nearby peaceful players, target filters, HP priority, MaxHP priority, cooldown/range and buff state.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
3. `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`
4. `analysis/17_BUFF_RUNTIME_SCHEMA.md`
5. `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
6. `features/AUTO_BUFF.md`
7. `database/NGAMY_SUPPORT_SKILLS.md`

## OPTIONAL

- Team-only data: `analysis/25_TEAM_RUNTIME_FOLLOW.md`.
- Older behavior/UX donor: `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md`.
- MainThread action execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.
- Orchestration with Train/Sell: `contexts/BUILD_ORCHESTRATOR.md`.

## VERIFIED data source

`Game.GetNearByPeacePlayers(limit)` exposes at least:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

Do not require party membership to build the read-only candidate list.

## Correct Nga My skill identity

- 406 = Phật Quang Phổ Chiếu
- 407 = **Xung Hư Dưỡng Khí**
- 408 = Khởi Tử Hồi Sinh
- 423 = **Kim Châm Độ Kiếp**
- 424 = Thanh Tâm Phổ Thiện Chú

Legacy Lua variable `KIMCHAMDOKIEP=407` is misleading. Never label 407 as real Kim Châm in new code.

## Donor action path

Built-in team support demonstrates:

`CheckCondition -> GetSkillLuaData -> distance/CastRange -> ChaseTarget if needed -> RequestUsingSkillWithTarget(skillID, RoleID)`.

Use cooldown readiness from `Game.GetSkillCooldown` before cast.

## Priority policy

Recommended deterministic flow:

1. fresh peaceful-player snapshot;
2. apply RoleID/name/guild/faction/level filters;
3. compute HP%;
4. filter below threshold;
5. select one target by policy (for example MaxHP DESC or lowest HP%);
6. revalidate target immediately before action;
7. validate skill learned/condition/cooldown/range;
8. issue one cast/chase action;
9. wait state proof;
10. rescan.

Do not build a long cast queue from one stale scan.

## State proof

Preferred:

- fresh target HP changes/reaches threshold;
- skill cooldown becomes active after a previously-ready cast;
- progress/cast state is consistent;
- target leaves AOI -> invalidate/rescan.

## Remaining targeted proof

Static/Lua evidence does not yet prove every beneficial skill is accepted by server on every non-team peaceful target. Verify the intended skill/target policy once through the live MainThread bridge and record server/game outcome.

## Safety

Pause on Captcha, local death/Revival, loading/map transition or incompatible progress state.

## Completion criteria

Auto Buff is complete only when it uses structured nearby data, stable RoleID identity, correct skill IDs, semantic cooldown/range/action paths, one mutable action at a time and fresh state proof after each action.