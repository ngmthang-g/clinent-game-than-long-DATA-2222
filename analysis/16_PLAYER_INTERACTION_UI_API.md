# Player interaction UI/API surface

Status: **VERIFIED from `OtherRolePopup.lua`, `MainUI_OtherHeader.lua`, `Global_Constants.lua`, `TCPPacketDefine.lua`.**

This document extends the nearby-player schema with the exact actions the shipped client exposes when another player is selected.

## Selected-player popup data

`MainUI_OtherHeader` passes the current selected target object into:

`OtherRolePopup:Show(CurrentTarget)`.

`OtherRolePopup:SetData(data)` directly reads these player-target fields:

- `RoleID`
- `Name`
- `Avarta`
- `Level`
- `FactionID`
- `TeamID`
- `GroupID`
- `GuildID`
- `GuildRank`
- `AlliesID`.

The popup also compares against local-player state such as:

- `Game.RoleData.TeamID`
- `GroupID`
- `GuildID`
- `GuildRank`
- `AlliesID`
- `IsAlliesHost`.

This is additional evidence that a selected-player object contains social/group state far beyond HP alone.

## Exact `C_OtherRoleCommand` values

From `Global_Constants.lua`:

| Command | Value |
|---|---:|
| RoleInfo | 1 |
| InviterOtherToGuild | 2 |
| GuildJoinRequest | 3 |
| PKChallenger | 4 |
| TeamInviter | 5 |
| AddFriend | 6 |
| Trade | 7 |
| Proclaim | 8 |
| TeamRequestJoin | 9 |
| GroupInvite | 10 |
| GroupRequestJoin | 11 |

Packet:

`CMD_OTHER_ROLE_COMMAND = 200051`.

## Exact UI-level actions by RoleID

### Browse player equipment/info

`OtherRolePopup:BtnBroweseEquipInfoClick()` sends:

`CMD_GET_OTHER_ROLE_INFO = 200066`

payload:

`RoleID`

Response opens/replaces `OtherRoleInfo` through `TCPCmdHandler`.

### Add friend/enemy/blacklist

Packet:

`CMD_ADD_FRIEND = 100012`

payload:

`FriendType:RoleID`

The same route handles Friend, Enemy and Black list types.

### Trade invitation

`CMD_OTHER_ROLE_COMMAND`

payload:

`C_OtherRoleCommand.Trade:C_TradeCommand.Request:RoleID`

Note that Trade uses a three-field form in this handler.

### Invite target to team

`CMD_OTHER_ROLE_COMMAND`

payload:

`C_OtherRoleCommand.TeamInviter:RoleID`

### Request to join target's team

payload:

`C_OtherRoleCommand.TeamRequestJoin:RoleID`

### Invite to guild

payload:

`C_OtherRoleCommand.InviterOtherToGuild:RoleID`

### Request to join guild

payload:

`C_OtherRoleCommand.GuildJoinRequest:RoleID`

### Group/legion invite and request

- invite: `C_OtherRoleCommand.GroupInvite:RoleID`
- request join: `C_OtherRoleCommand.GroupRequestJoin:RoleID`.

### Proclaim/force PK

payload:

`C_OtherRoleCommand.Proclaim:RoleID`.

### Challenge

Packet:

`CMD_CHALLENGE = 200075`

payload:

`C_ChallengeAction.Request:RoleID:useRandomArdorBuff`

where the third field is `0` for normal challenge or `1` for random Ardor buff option.

### Double ride invitation

Uses a direct Game API:

`Game.SendInviteDoubleRide(RoleID)`.

## Allies actions

The popup also exposes:

- `CMD_ALLIES_ASK_JOIN = 200115`
- `CMD_ALLIES_INVITER_JOIN = 200114`

with target/local Allies IDs in the payloads constructed by Lua.

## Automation relevance

The important architectural point is not to automate every social action. It is that **the player selected by RoleID is already represented by a rich semantic TargetData object and the UI invokes actions directly from that object**.

For a nearby-player tool this enables:

- stable RoleID-based selection;
- direct lookup of Team/Guild/Group relationships;
- optional player-info request when deeper data is needed;
- avoiding screen-coordinate interactions with player models or popup buttons.

## Safety/eligibility rule

Do not assume every action is always legal. The popup itself shows/hides buttons according to local/target Team/Guild/Group state, and the server remains authoritative. Any external action controller should reproduce relevant eligibility guards or simply rely on server rejection without spamming repeated requests.
