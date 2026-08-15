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

## Verified Nga My healing/support skill IDs

Cross-checking `Global_Constants.lua`, `AutoHp_Layout.xml` and `Skills.xml` gives:

- Phật Quang Phổ Chiếu = `406`
- **Xung Hư Dưỡng Khí = `407`**
- Khởi Tử Hồi Sinh = `408`
- **Kim Châm Độ Kiếp = `423`**
- Thanh Tâm Phổ Thiện Chú = `424`.

Important frozen-client quirk: the built-in Lua constant/config key called `KIMCHAMDOKIEP` / `KimChamDoKiep` points to **407**, but the visible AutoHp UI text for that toggle says **Xung Hư Dưỡng Khí**, and Config confirms actual Kim Châm Độ Kiếp is **423**.

So never identify skill 407 as Kim Châm based only on that legacy variable name.

Full correction/evidence: `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`.

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

`Game.GetBuffData(BuffID)` additionally exposes at least `Level` and `Stack`; `Game.GetBuffProperties(BuffID)` supplies semantic magic properties.

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

### v1.3.1 source donor — filter UX worth preserving

`ThanLongAutoBuff_Source_v1.3.1` was source-inspected separately in `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md`.

Its useful filter/product behavior should be retained:

- scan-and-tick lists rather than requiring manual text entry;
- player selection persisted by RoleID;
- faction selection persisted by FactionID;
- guild selection + RoleID + faction + level + MaxHP range + HP threshold composed together;
- selected entries remain configured when they temporarily leave AOI;
- self buff is an explicit independent option;
- per-client filter/profile isolation.

Do not copy the donor's direct `ObjectManager.sprites` scan when the semantic nearby-player API already exposes the needed data.

## Priority policy matching the requested behavior

A deterministic policy:

1. scan current eligible peaceful players;
2. filter HP% below threshold;
3. sort by `MaxHP DESC`;
4. select the highest-MaxHP low-HP target;
5. issue at most one heal action;
6. wait for state proof;
7. rescan current players/HP;
8. continue/reselect according to fresh state.

Do not build a long queue from a stale scan.

### Priority modes recovered from the v1.3.1 donor

The source already implements three useful user-facing policies:

1. lowest HP% first;
2. highest MaxHP first;
3. lowest MaxHP first.

For the two MaxHP modes the donor locks the chosen RoleID until that target no longer qualifies. Preserve that behavior as an optional policy.

Recommended improvement: add an optional `CriticalHPPercent` emergency override so a player at critically low HP may temporarily preempt the locked MaxHP target, then return to the locked target afterward if still eligible.

## Skill selection policy

The tool should expose semantic skill choices by **actual name + SkillID**, not copy misleading internal option names.

For the user's primary desired spell:

- Thanh Tâm Phổ Thiện Chú -> `424`.

Other candidates:

- Phật Quang Phổ Chiếu -> `406`
- Xung Hư Dưỡng Khí -> `407`
- Kim Châm Độ Kiếp -> `423` (static Config verified; not used by built-in AutoHp fallback)
- Khởi Tử Hồi Sinh -> `408` for dead eligible target.

If reproducing the built-in AutoHp fallback order exactly, it is:

`406 -> 424 -> 407`

where 407 is Xung Hư Dưỡng Khí.

For a custom tool, let the user choose priority rather than assuming the built-in order is always desired.

Before casting any selected ID:

- `Game.HasSkill(skillID)` where appropriate;
- cooldown ready;
- `Game.CheckCondition(skillID)`;
- target alive/dead eligibility;
- range/path eligibility.

### Skill discovery donor

The v1.3.1 source dynamically enumerates the current character's owned skills and keeps the choice per session. Preserve this UI behavior, but resolve semantic identity by verified SkillID first. Dynamic enumeration is for ownership/UI, not a reason to fuzzy-match an already known canonical skill ID.

## Exact Config semantics useful for range/timeouts

- 406: SelfAndAlly, CastRange 15, AttackRadius 7, ProgressTime 3000 ms.
- 407: PeacePlayer, CastRange 15, ProgressTime 3000 ms.
- 408: PeacePlayer, CastRange 3, ProgressTime 10000 ms.
- 423: PeacePlayer, CastRange 15, ProgressTime 0.
- 424: PeacePlayer, CastRange 15, ProgressTime 1000 ms.

Do not use a single fixed 500 ms timeout for all of these skills.

## Range handling

Use skill data, not F-key assumptions:

1. `skillData = Game.GetSkillLuaData(skillID)`;
2. convert CastRange through `Game.CellToDistance` as the built-in donor does;
3. compare real target distance;
4. if outside range, call `Game.ChaseTarget`;
5. cast from success callback;
6. if already in range, cast immediately.

## Revalidate immediately before cast

One strong behavior from the v1.3.1 source is to re-read/re-check the chosen target just before the mutable request. Preserve this pattern in the new architecture:

```text
fresh candidate snapshot
 -> choose RoleID
 -> acquire single action slot
 -> re-read current target by RoleID
 -> re-check HP/MaxHP + threshold
 -> re-check Peace
 -> re-apply latest filters
 -> check skill ownership/cooldown/condition
 -> range/chase check
 -> dispatch one semantic cast on Unity main thread
```

Do not assume a target selected 300–500 ms earlier is still valid.

## State proof after a heal cast

Preferred order:

1. fresh target HP differs / reaches threshold;
2. skill cooldown transition as secondary evidence;
3. progress/cast state consistent with the exact skill;
4. target disappears/out of AOI -> invalidate and rescan.

Do not simply `Sleep(500)` and assume success.

The v1.3.1 donor's `commandsSent` counter measures requests issued, **not confirmed healing**. Keep separate counters such as `healsRequested` and `healsProven`.

## Pacing / anti-spam

The donor used 2.5 seconds per target and 700 ms globally. Keep those only as prototype/rate-limit guards. Exact cooldown, ProgressTime and state proof should drive normal pacing.

## Metadata cache behavior

The donor contains a useful failure-cache rule: valid metadata can live longer, but blank/fallback results get only a short TTL and are retried quickly. Preserve the principle:

- stable name / faction display metadata: longer cache;
- guild data: shorter cache;
- blank/error/transient result: very short cache;
- IDs remain canonical identity whenever available.

## Persistent self-buffs

For local-player buffs, use:

- `Game.HasBuff(skillID)` for the lightweight built-in check;
- `Game.GetBuffs()` when duration/stack is needed;
- AddBuff/UpdateBuff/RemoveBuff events as state proof.

A policy can refresh only when absent or when `DurationTick` falls below a configured threshold.

## Target persistent buffs

Current Lua proof for other players is limited to:

`Game.GetTargetBuffIcons(RoleID)`.

Until a structured target BuffID/duration API is found, do not repeatedly cast persistent buffs based solely on uncertain icon matching. HP-based healing is much better grounded today.

## Self-heal

Built-in code treats self separately and uses targetRoleID `-1` with `RequestUsingSkillWithTarget` when self HP is below threshold. Keep self-support as an explicit policy option.

The v1.3.1 donor also correctly separates self from nearby-player Peace filtering, but its exact self RoleID request behavior is not a substitute for the shipped semantic donor; use the canonical built-in semantics.

## Multi-client rule

For every game process keep separate nearby snapshot, selected targets, settings/profile, current action, cooldown snapshot and Unity dispatcher context. Never share client pointers between processes.

The v1.3.1 source's one-`GameSession`-per-PID model is a good behavioral donor. Improve persistence by binding reusable profiles to RoleID/profile identity rather than PID alone because PID changes after restart.

## Observability

Retain per-client live diagnostics from the v1.3.1 source, but expand them with state proof:

```text
nearbyPeace
matchedFilter
lowHP
currentTarget
currentAction
lastActionResult
lastStateProof
healsRequested
healsProven
mapReady
progressActive
captcha
dispatcherReady
```

This makes “Auto is not buffing” diagnosable without guessing.

## Safety guards

Before mutable action:

- Captcha active -> pause and require user interaction;
- loading/map transition -> wait;
- local player dead/Revival -> revive state machine;
- progress/channel action active -> wait unless feature-specific interruption is safe;
- target stale/out of AOI -> rescan;
- skill unavailable/condition false/cooldown active -> do not cast.

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

## Legacy donor mechanism explicitly rejected

Do not migrate these parts of v1.3.1 into the new action engine:

- `CreateRemoteThread` remote worker;
- direct arbitrary mutable IL2CPP calls from that worker;
- hardcoded RVA/offset as sole runtime identity;
- direct `ObjectManager.sprites` enumeration as first-choice scanner;
- request-count-as-success semantics;
- missing range/chase and global Captcha/loading/progress guards.

Full source audit: `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md`.

## What is NOT needed

- party membership for the read list;
- OCR of player names/HP bars;
- CE scanning HP offsets;
- clicking a player on screen;
- pressing F1 physically;
- hardcoded cooldown delays;
- stale UI button pointers.

## Integration with higher-level automation

Auto Buff should be one feature policy under `features/AUTO_ORCHESTRATOR.md`, not a competing independent mutable-action loop. The orchestrator arbitrates Buff vs Train vs Party vs Revive vs Sell vs map/spot changes for each PID.

## Remaining runtime proof

Before declaring the complete external non-team feature VERIFIED:

1. invoke/read `GetNearByPeacePlayers` through the actual bridge;
2. confirm return object fields in the runtime bridge;
3. prove `RequestUsingSkillWithTarget` on a selected non-team peaceful RoleID through the Unity/main-thread dispatcher;
4. verify server/game accepts the intended beneficial skill on that target;
5. verify range/chase behavior;
6. verify target disappearance/map-transition safety;
7. record outcome/state proof and edge cases.
