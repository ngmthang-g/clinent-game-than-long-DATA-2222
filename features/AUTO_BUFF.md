# Feature specification — Auto Buff / Nga My support nearby players

Status: **read/query schema + donor action logic + skill cooldown/local buff schema VERIFIED; external non-team buff loop requires runtime integration proof**.

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

## Verified cooldown source

The shipped SkillBar calls:

`Game.GetSkillCooldown(skillID)`

and reads:

- `[1] = passedTicks`
- `[2] = cooldownTicks`.

Ready condition:

`cooldownTicks <= 0 OR passedTicks >= cooldownTicks`.

So before requesting a cast, the tool can add an explicit cooldown readiness check rather than retrying on a timer.

Full detail: `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`.

## Verified local buff state

For the local role the game exposes:

`Game.GetBuffs()`

with live fields:

- `BuffID`
- `DurationTick` (milliseconds)
- `Stack`.

`Game.GetBuffData(BuffID)` additionally exposes at least:

- `Level`
- `Stack`.

`Game.GetBuffProperties(BuffID)` supplies semantic magic properties.

This is useful for self-buff maintenance and cast verification. Arbitrary target players are only VERIFIED to expose buff icons so far; do not pretend we already have their structured BuffID/duration list.

Full detail: `analysis/17_BUFF_RUNTIME_SCHEMA.md`.

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
5. issue at most one heal action;
6. wait for state proof;
7. rescan current players/HP;
8. continue the same target only while it is still below threshold and remains the chosen policy winner;
9. otherwise choose the next highest-MaxHP eligible target.

Do not build a long queue from a stale scan.

## Skill selection

For a living target needing healing:

1. 406 if enabled, learned/available, cooldown ready and `Game.CheckCondition(406)` passes;
2. otherwise 424 under the same checks;
3. otherwise 407;
4. otherwise no action.

If exact dead state is available and Cải Tử Hoàn Sinh is enabled:

- validate skill 408 condition/cooldown;
- use semantic target action for RoleID.

The 406 -> 424 -> 407 preference order mirrors the built-in donor implementation.

## Range handling

Never assume F1 or keyboard range.

Use skill data:

1. `skillData = Game.GetSkillLuaData(skillID)`;
2. convert `skillData.CastRange` through `Game.CellToDistance` as the built-in donor does;
3. compare real target distance;
4. if outside range, call `Game.ChaseTarget`;
5. cast from the success callback;
6. if already inside range, cast immediately.

## State proof after a heal cast

Preferred order:

1. fresh target HP differs / target reaches threshold;
2. skill cooldown transitions from ready to active as secondary evidence;
3. cast/progress state confirms action was accepted;
4. target disappears/out of AOI -> invalidate and rescan.

Do not simply `Sleep(500)` and assume success.

## Persistent self-buffs

For local-player buffs, use:

- `Game.HasBuff(skillID)` for the lightweight check used by built-in Auto;
- `Game.GetBuffs()` when duration/stack is needed;
- AddBuff/UpdateBuff/RemoveBuff events as state proof.

A policy can refresh a buff only when:

- absent; or
- remaining `DurationTick` is below a user-configured refresh threshold.

Do not recast every scan loop.

## Target persistent buffs

Current Lua proof for other players is limited to:

`Game.GetTargetBuffIcons(RoleID)`.

Until a structured target BuffID/duration API is found, do not implement repeated target-buff recasting based only on uncertain icon matching. Healing by HP is much better grounded today.

## Self-heal

Built-in code treats self separately and uses targetRoleID `-1` with `RequestUsingSkillWithTarget` when self HP is below threshold. Keep self-support as an explicit policy option rather than mixing the local player into the nearby list implicitly.

## Multi-client rule

For every game process keep separate:

- nearby snapshot;
- selected targets;
- settings/profile;
- current action;
- last scan/cast timestamps;
- cooldown snapshot;
- Unity dispatcher context.

Never share client pointers between processes. Only static IDs/config may be shared.

## Safety guards

Before mutable action:

- Captcha active -> pause and require user interaction;
- loading/map transition -> wait;
- local player dead/Revival -> hand over to revive state machine;
- progress/channel action active -> wait unless the specific action permits interruption;
- selected target stale/out of AOI -> rescan;
- skill not learned / condition false / cooldown active -> do not cast.

See `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`.

## Architecture

```text
Resolver
 -> read-only NearbyPlayerScanner
 -> Snapshot Store
 -> Filter/Priority Observer
 -> Cooldown/Buff Observer
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
- hardcoded skill cooldown delays;
- holding a stale UI button pointer.

## Remaining runtime proof

Before declaring the complete external non-team feature VERIFIED:

1. invoke/read `GetNearByPeacePlayers` through the actual bridge;
2. confirm return object fields in the runtime bridge;
3. prove `RequestUsingSkillWithTarget` on a selected non-team peaceful RoleID through the Unity/main-thread dispatcher;
4. verify server/game accepts the intended beneficial skill on that target;
5. record outcome/state proof and edge cases.

If step 3/4 reveals game/server eligibility restrictions, keep the scanner and filter model but enforce those restrictions in Safety Guard.
