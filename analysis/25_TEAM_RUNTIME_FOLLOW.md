# Team runtime / follow mode / team-member schema

Status: **VERIFIED from decrypted `MiniBox_MiniTeamFrame.lua`, `TeamRole.lua`, `TeamInvite.lua`, `AutoFight_Main.lua`, `Global_Constants.lua`, `TCPCmdHandler.lua`, `TCPCmdEventHandler.lua`.**

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

## Exact team action constants

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

Packet: `CMD_TEAM_ACTION`.

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

These are documented for protocol understanding. Destructive/social mutations should not be used by generic Auto Train/Buff logic unless the user explicitly requests them.

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

There are now two distinct verified friendly-player sources:

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

## Future AI rule

Do not rediscover party member HP by CE scanning. The shipped UI already documents exact structured team HP/MaxHP and nearby-position data paths.
