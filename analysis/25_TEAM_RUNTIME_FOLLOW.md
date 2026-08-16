# Team runtime / follow mode / team-member schema

Status: **VERIFIED from decrypted `MiniBox_MiniTeamFrame.lua`, `TeamRole.lua`, `TeamInvite.lua`, `OtherRolePopup.lua`, `AutoFight_Main.lua`, `Global_Constants.lua`, `TCPCmdHandler.lua`, `TCPCmdEventHandler.lua`.**

## Team state object

The client keeps current team state in global `C_TeamData` while `Game.RoleData.TeamID > 0`.

Fields directly consumed by shipped UI/Auto code include:

### Team-level

- `C_TeamData.LeaderID`
- `C_TeamData.TeamMember[]`.

### Team member

Observed fields:

- `RoleID`
- `RoleName`
- `Level`
- `FactionID`
- `MapID`
- `Hp`
- `MaxHp`
- `AvartaID`
- `PosX`
- `PosY`.

The compact team UI renders exact `Hp/MaxHp` and calls `Game.GetTargetBuffIcons(RoleID)` for up to six visible buff icons.

Clicking a team member uses `Game.SelectTarget(RoleID)`.

## Team data event lifecycle

`G_TCPEventType.UpdateTeamData` updates `C_TeamData` directly.

- if event data is `"Disband"`, team-side transient lists are cleared;
- otherwise `C_TeamData = data` and open team UI is refreshed.

This means a per-process Team Snapshot can be event-driven rather than polling UI pixels.

## Exact `C_TeamAction` constants

`C_TeamAction`:

| Action | Value |
|---|---:|
| CreateTeam | 0 |
| Kick | 1 |
| Disband | 2 |
| ChangLeader | 3 |
| LeaveTeam | 4 |
| AcceptJoin | 5 |
| RejectJoin | 6 |
| RequestJoin | 7 |
| AcceptInvite | 8 |
| RejectInvite | 9 |
| RequestInvite | 10 |

Packet family: `CMD_TEAM_ACTION`.

Observed payload forms include:

- create: `0`
- disband: `2`
- leave: `4:selfRoleID`
- change leader: `3:selectedRoleID`
- kick: `1:selectedRoleID`
- accept join: `5:roleID`
- reject join: `6:roleID`
- accept invite: `8:leaderID`
- reject invite: `9:leaderID`.

The numeric existence of `C_TeamAction.RequestJoin=7` is VERIFIED, but this document does **not** invent a `CMD_TEAM_ACTION` payload for it when that payload was not directly observed in the inspected team handler.

## Exact request-to-join route from selected-player popup

This previously looked like a remaining gap, but `OtherRolePopup.lua` already gives a complete legitimate UI path.

Packet:

`CMD_OTHER_ROLE_COMMAND = 200051`

Relevant command enum:

`C_OtherRoleCommand.TeamRequestJoin = 9`

When the user chooses **request to join the selected player's team**, shipped Lua sends:

```text
C_OtherRoleCommand.TeamRequestJoin : RoleID
```

Therefore the exact payload is:

```text
9:targetRoleID
```

This is **VERIFIED source-level construction**.

### Related selected-player team action

Invite the selected player to the local team uses:

```text
C_OtherRoleCommand.TeamInviter = 5
CMD_OTHER_ROLE_COMMAND = 200051
payload = 5:targetRoleID
```

### Important distinction between the two enum families

Do not confuse:

```text
C_TeamAction.RequestJoin = 7
```

with:

```text
C_OtherRoleCommand.TeamRequestJoin = 9
```

They belong to different action/packet layers. For an external auto that already has a candidate player's RoleID, the **selected-player popup donor route `200051 / 9:RoleID` is an exact proven request-to-join path** and does not need another broad trace.

Server acceptance is still asynchronous and must be proven by fresh `Game.RoleData.TeamID` / `C_TeamData` update, not merely by the request being sent.

## Recommended automatic join flow

```text
fresh nearby/team-leader candidate RoleID
 -> verify local role currently not in a team (or policy explicitly leaves first)
 -> send CMD_OTHER_ROLE_COMMAND 200051 payload 9:targetRoleID
 -> wait UpdateTeamData / TeamID change
 -> if accepted: publish new TeamSnapshot
 -> if rejected/timeout: cooldown that RoleID and optionally try next candidate
```

Do not send join requests to every nearby player on every scan.

## Built-in Follow mode

`TeamRole:ButtonFollowClicked()` does not simulate movement keys. It calls:

`GUI.FindUI("AutoFight_Main"):TurnOnFollowTarget(SelectedMemberID)`.

`AutoFight_Main` stores a semantic `FollowTarget` RoleID.

### Nearby teammate path

Once per scan loop it calls:

`Game.GetNearTeammates(self:GetCurrentPosition(), true)`.

If the target teammate is currently in radar/AOI, the returned record provides at least:

- `RoleID`
- `Name`
- `Position`.

The engine follows using:

`Game.MoveTo(Position.X, Position.Y)`.

### Out-of-radar fallback

If the member is absent from the nearby teammate list, it falls back to `C_TeamData.TeamMember` and uses:

`Game.GoTo(Member.MapID, Member.PosX, Member.PosY, callback)`.

This is important: team data can provide coarse cross-map follow state while nearby world data provides precise local position.

## Maps where built-in Follow is explicitly rejected

The shipped source blocks follow on MapIDs:

`10000, 10004, 10005, 10007, 10014, 10015, 10016, 10017`.

Do not silently remove this restriction in a derivative controller without understanding why those maps are special.

## Auto Buff relevance

There are two distinct verified friendly-player sources:

1. `Game.GetNearByPeacePlayers(limit)` — nearby peaceful players, independent of party UI;
2. team-specific state — `C_TeamData` + `Game.GetNearTeammates(...)`.

For team members the client additionally has:

- exact team membership/leader state;
- map/backup position;
- precise nearby `Position` when in AOI;
- HP/MaxHP;
- target buff icons.

A robust support controller can prefer live nearby objects for range/casting and use team data only as backup/navigation metadata.

## Snapshot rule

Copy semantic values into the external tool's own snapshot. Do not retain a Lua/C# team-member object or pointer across updates/map transitions.

Recommended fields:

```text
RoleID
RoleName
Level
FactionID
MapID
HP
MaxHP
PosX/PosY backup
NearbyPosition optional
IsLeader
BuffIcons optional
LastUpdateTick
```

## Social-action safety rule

Kick, Disband, LeaveTeam, invite and join requests are real social mutations. Only run them when the active tool policy explicitly requests them, one mutation at a time, with anti-spam cooldowns and server-state proof.

## Future AI rule

Do not rediscover party member HP by CE scanning. Do not re-trace the selected-player request-to-join action: `CMD_OTHER_ROLE_COMMAND=200051`, payload `9:targetRoleID` is already recovered from shipped Lua.