# Feature specification — Auto Buff / Nga My support nearby players

Status: **read/query schema + donor action logic VERIFIED; external non-team buff loop requires runtime integration proof**.

## Goal

Support selected friendly players around the character without relying on party-only UI, screen recognition or Cheat Engine value scans.

## Verified data source for nearby peaceful players

The stock client UI calls:

`Game.GetNearByPeacePlayers(MaxPlayers)`

and directly reads each returned player's:

- `RoleID`
- `Name`
- `Level`
- `FactionID`
- `HP`
- `MaxHP`
- `GuildName`
- `AvartaID`
- `TeamRank`.

This proves the scanner data required for Name/ID/Faction/Guild/HP/MaxHP filters is already available as structured game data for nearby peaceful players.

## Verified Nga My skill IDs

- Phật Quang Phổ Chiếu = `406`
- Thanh Tâm Phổ Thiện Chú = `424`
- Kim Châm Độ Kiếp = `407`
- Cải Tử Hoàn Sinh = `408`.

## Verified donor action path

The built-in team's support engine uses:

- `Game.CheckCondition(skillID)`
- `Game.GetSkillLuaData(skillID)`
- `Game.GetDistance(target.Position, selfPosition)`
- `Game.CellToDistance(SkillData.CastRange)`
- `Game.ChaseTarget(RoleID, range, success, fail, true)`
- `Game.RequestUsingSkillWithTarget(skillID, RoleID)`.

This is the preferred semantic action pattern.

## Recommended read-only candidate snapshot

Normalize each scanned player into the tool's own immutable snapshot:

```text
RoleID
Name
Level
FactionID / FactionName
GuildName
HP
MaxHP
HPPercent
TeamRank
LastSeenTick
```

If the runtime object exposes Position during implementation, copy it too; do not keep the original client object/pointer beyond the read step.

## Filtering model

Support at least:

- explicit RoleID whitelist;
- selected names;
- guild;
- faction;
- minimum/maximum level if desired;
- HP below configured percent;
- alive/dead state when exact field is available;
- optional MaxHP priority.

## Priority policy matching the requested behavior

A deterministic policy:

1. scan current eligible peaceful players;
2. filter HP% below threshold;
3. sort by `MaxHP DESC`;
4. select the highest-MaxHP low-HP target;
5. heal until target reaches threshold or action is no longer appropriate;
6. rescan;
7. choose next highest-MaxHP eligible target.

Do not build a long queue from a stale scan. Rescan after every mutable action.

## Skill selection

If target is alive and needs healing:

1. if enabled + condition passes -> 406;
2. else if enabled + condition passes -> 424;
3. else if enabled + condition passes -> 407;
4. else no action.

If exact dead state is available and Cải Tử Hoàn Sinh is enabled:

- condition check `408`;
- use semantic target action for RoleID.

The exact preference order above mirrors the built-in donor implementation for normal healing.

## Range handling

Never assume F1 or keyboard range.

Use skill data:

1. `skillData = Game.GetSkillLuaData(skillID)`;
2. convert `skillData.CastRange` through `Game.CellToDistance`;
3. compare real target distance;
4. if outside range, call `Game.ChaseTarget`;
5. cast from its success callback;
6. if already inside range, cast immediately.

## State proof after a cast

Prefer one or more of:

- target HP changes in a fresh nearby-player snapshot;
- relevant buff event/data appears;
- target becomes invalid/out of AOI;
- skill condition/cooldown state changes consistently;
- explicit cast/game state confirms completion.

Do not simply `Sleep(500)` and assume success.

## Self-heal

Built-in code treats self separately and uses targetRoleID `-1` with `RequestUsingSkillWithTarget` when self HP is below threshold. Keep self-support as an explicit policy option rather than mixing the local player into the nearby list implicitly.

## Multi-client rule

For every game process keep separate:

- nearby snapshot;
- selected targets;
- settings/profile;
- current action;
- last scan/cast timestamps;
- Unity dispatcher context.

Never share client pointers between processes. Only static IDs/config may be shared.

## Architecture

```text
Resolver
 -> read-only NearbyPlayerScanner
 -> Snapshot Store
 -> Filter/Priority Observer
 -> Buff State Machine
 -> Safety Guard
 -> Action Queue (max 1)
 -> Unity/Main Thread Dispatcher
 -> RequestUsingSkillWithTarget / ChaseTarget
 -> state proof
 -> rescan
```

## What is NOT needed

- party membership for the read list;
- OCR of player names/HP bars;
- CE scanning HP offsets;
- clicking a player on screen;
- pressing F1 physically;
- holding a stale UI button pointer.

## Remaining runtime proof

Before declaring the complete external feature VERIFIED:

1. invoke/read `GetNearByPeacePlayers` through the actual bridge;
2. confirm return object fields in the runtime bridge;
3. prove `RequestUsingSkillWithTarget` on a selected non-team peaceful RoleID through the Unity/main-thread dispatcher;
4. verify server/game accepts the intended beneficial skill on that target;
5. record outcome/state proof and edge cases.

If step 3/4 reveals game/server eligibility restrictions, keep the scanner and filter model but enforce those restrictions in Safety Guard.
