# Context Pack — Build Party / Team / Follow

## Scope

Use for team state, leader/member data, join/leave/invite/kick/change-leader actions and semantic Follow mode.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `analysis/25_TEAM_RUNTIME_FOLLOW.md`
4. `analysis/16_PLAYER_INTERACTION_UI_API.md`
5. `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`

## OPTIONAL

- Nearby-player detail: `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`.
- Map/follow detail: `analysis/22_MAP_MINIMAP_RUNTIME.md`.
- MainThread execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.
- Adaptive orchestration: `contexts/BUILD_ORCHESTRATOR.md`.

## VERIFIED team state

Current team state is represented by `C_TeamData` while local `Game.RoleData.TeamID > 0`.

Team/member fields include:

`LeaderID`, member `RoleID, RoleName, Level, FactionID, MapID, Hp, MaxHp, AvartaID, PosX, PosY`.

Nearby precise teammate position comes from `Game.GetNearTeammates(...)`.

## Exact join-party request — already solved

The shipped selected-player popup provides a complete request-to-join route:

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamRequestJoin = 9
payload = 9:targetRoleID
```

This is source-level VERIFIED. Do **not** broad-trace team joining again merely to rediscover this request.

After sending, success proof is asynchronous:

```text
Game.RoleData.TeamID changes to a valid team
AND/OR
C_TeamData / UpdateTeamData reflects membership
```

Request sent != accepted.

### Related invite route

Invite a selected player to the local team:

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamInviter = 5
payload = 5:targetRoleID
```

## Exact `C_TeamAction` constants

A separate team-action enum also exists:

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

Observed leave request:

`CMD_TEAM_ACTION`, payload `4:selfRoleID`.

Do not confuse `C_TeamAction.RequestJoin=7` with the proven selected-player popup command `C_OtherRoleCommand.TeamRequestJoin=9`; they are different protocol/action families.

## Follow mode

Built-in semantic follow uses:

`GUI.FindUI("AutoFight_Main"):TurnOnFollowTarget(RoleID)`.

When target is nearby it follows live Position with `Game.MoveTo`; when out of AOI it can use team MapID/PosX/PosY backup through `Game.GoTo`.

## Party-join policy

Recommended production flow:

```text
fresh candidate RoleID
 -> ensure local role not already in incompatible team state
 -> send ONE 200051 / 9:RoleID request
 -> wait team-state proof
 -> if rejected/timeout, cooldown candidate
 -> optionally try next candidate
```

Never spam every visible player every scan.

Candidate sources can include nearby peaceful players or nearby team-leader data where appropriate.

## Destructive/social action rule

Kick, Disband, LeaveTeam and leadership changes are real user/social mutations. Use them only when the requested feature/policy explicitly calls for them.

## Completion criteria

Stable RoleID identity, event/state-driven membership proof, anti-spam cooldowns, one social mutation at a time, and no screen-coordinate party UI automation when semantic actions already exist.