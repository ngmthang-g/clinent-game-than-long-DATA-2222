# Context Pack — Build Party / Team / Follow

## Scope

Use for team state, leader/member data, join/leave/invite/kick/change-leader actions and semantic Follow mode.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/25_TEAM_RUNTIME_FOLLOW.md`
3. `analysis/16_PLAYER_INTERACTION_UI_API.md`
4. `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
5. `analysis/22_MAP_MINIMAP_RUNTIME.md`

## OPTIONAL

- MainThread execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.
- Adaptive orchestration: `contexts/BUILD_ORCHESTRATOR.md`.

## VERIFIED team state

Current team state is represented by `C_TeamData` while local `Game.RoleData.TeamID > 0`.

Team/member fields include:

`LeaderID`, member `RoleID, RoleName, Level, FactionID, MapID, Hp, MaxHp, AvartaID, PosX, PosY`.

Nearby precise teammate position comes from `Game.GetNearTeammates(...)`.

## Exact team action constants

`C_TeamAction`:

- CreateTeam=0
- Kick=1
- Disband=2
- ChangeLeader=3
- LeaveTeam=4
- AcceptJoin=5
- RejectJoin=6
- RequestJoin=7
- AcceptInvite=8
- RejectInvite=9
- RequestInvite=10.

Observed leave payload: `4:selfRoleID`.

## Follow mode

Built-in semantic follow uses:

`GUI.FindUI("AutoFight_Main"):TurnOnFollowTarget(RoleID)`.

When target is nearby it follows live Position with `Game.MoveTo`; when out of AOI it can use team MapID/PosX/PosY backup through `Game.GoTo`.

## Party-join policy

Use fresh nearby/team-leader data, choose one candidate, send one request, wait team-state proof, then cooldown/retry another candidate if needed. Never spam every visible player every scan.

## Destructive/social action rule

Kick, Disband, LeaveTeam and leadership changes are real user/social mutations. Use them only when the requested feature/policy explicitly calls for them.

## State proof

Use current `Game.RoleData.TeamID`, `C_TeamData`, leader/member updates or relevant team event state. “Request sent” is not “server accepted”.

## Completion criteria

Stable RoleID identity, event/state-driven membership proof, anti-spam cooldowns, one social mutation at a time, and no screen-coordinate party UI automation when semantic actions already exist.