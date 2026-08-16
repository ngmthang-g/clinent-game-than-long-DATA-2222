# Feature specification — Adaptive Auto Orchestrator

Status: **DESIGN SYNTHESIS** built from VERIFIED semantic APIs + Auto Buff v1.3.1 behavior donor + current requested automation ideas. Individual actions retain the confidence level of their underlying KB evidence; the full end-to-end orchestrator is not yet runtime VERIFIED.

## Goal

Coordinate Auto Train, Party, Auto Buff, Revive, Bag/Sell and map/spot switching as **one state machine per game client**.

The important design change is that features must not run as unrelated loops/threads that issue mutable actions concurrently. Scanners may run read-only, but each client gets **at most one mutable action in flight**.

## 1. Top-level states

Recommended state family:

```text
IDLE
PRECHECK
TRAVEL_TO_SPOT
WAIT_MAP_READY
ARRIVE_SPOT
PARTY_DISCOVERY
PARTY_REQUEST
START_TRAIN
TRAINING
BUFF_SUPPORT
REVIVAL
BAG_EVALUATION
SELLING
SPOT_EVALUATION
CHANGE_SPOT
PAUSED_CAPTCHA
RECOVERY
ERROR
```

A feature may have its own inner state machine, but all mutable actions go through the same per-client action gate.

## 2. Train spot profile

Each configured train spot should be a first-class record, not only an X/Y pair.

```text
SpotID
Name
MapID
TrainX
TrainY
Tolerance
TrainRadius
PreferredVendor / vendor policy
PartyPolicy
Enabled
Priority
CooldownUntil / BadUntil
```

Runtime metrics:

```text
VisitStartedAt
DeathsRolling30m
LootEventsRolling30m
LootValueRolling30m
FreeBagStart
FreeBagNow
TrainSeconds
IdleSeconds
PartyFoundCount
PartyJoinAttempts
PartyJoinSuccess
LastVisitedAt
LastFailureReason
SpotScore
```

## 3. Cross-map travel

Use semantic navigation already VERIFIED:

```text
StartAutoFight(None)
 -> wait Train state stopped
 -> Game.GoTo(MapID, X, Y)
 -> wait expected MapID
 -> wait Game.IsMapReady() == true
 -> wait valid RoleData.Position
 -> wait distance(Position, TrainPoint) <= tolerance
 -> continue
```

Do not use a fixed post-map sleep as success proof.

Use `GetCurrentMoveDestination()` for diagnostics and movement-state proof when needed.

## 4. Party behavior on arrival

Requested behavior:

```text
arrive spot
 -> optionally leave old party
 -> scan nearby players/team leaders
 -> determine party state
 -> request to join an eligible party
 -> wait for state proof / timeout
 -> start training regardless according to policy
```

### Data/actions already grounded

- nearby peaceful players are available from `Game.GetNearByPeacePlayers(MaxPlayers)`;
- selected-player data exposes `TeamID` and other social IDs;
- `GetNearbyTeamLeaders` exists as a useful candidate query;
- current team state is in `C_TeamData` and `Game.RoleData.TeamID`;
- `C_TeamAction.LeaveTeam = 4`;
- observed exact leave payload is `4:selfRoleID` through `CMD_TEAM_ACTION`;
- the team action enum also contains `RequestJoin=7`, `AcceptJoin=5`, `RejectJoin=6`, `AcceptInvite=8`, `RejectInvite=9`, etc.; only use payload forms that are actually documented/verified for the requested operation.

Canonical team evidence: `analysis/25_TEAM_RUNTIME_FOLLOW.md`.

### Anti-spam policy

Never request every visible player continuously.

Recommended party request state:

```text
candidate leaders sorted by policy
 -> send one request
 -> wait server/team-state proof
 -> if rejected/timeout, cooldown that RoleID
 -> try next candidate
 -> cap attempts per arrival / per time window
```

## 5. Buff eligibility policy

Auto Buff should reuse the mature donor filter model:

- explicit RoleID whitelist;
- selected names for display/convenience;
- guild;
- faction;
- level range;
- MaxHP range;
- HP threshold;
- include self;
- priority mode.

Recommended stable identity:

- character selection: RoleID;
- faction selection: FactionID;
- guild: prefer GuildID if/when resolved reliably; fall back to normalized guild name only when GuildID is unavailable.

Examples requested:

```text
only buff RoleID A/B/C
OR only buff selected names
OR only buff GuildName == ABC
OR combine guild + faction + MaxHP range + HP threshold
```

## 6. Buff priority policy

Supported modes from the v1.3.1 donor:

1. lowest HP% first;
2. highest MaxHP first with target lock;
3. lowest MaxHP first with target lock.

Recommended extension:

```text
CriticalHPPercent emergency override
```

This allows a critical player to preempt a locked MaxHP target temporarily.

Every cast must:

```text
select from fresh snapshot
 -> revalidate RoleID still present
 -> re-read HP/MaxHP
 -> re-check Peace and filters
 -> check skill ownership/condition/cooldown
 -> check map/death/progress/Captcha guards
 -> ensure range or ChaseTarget
 -> dispatch exactly one cast on Unity main thread
 -> wait state proof
 -> rescan
```

## 7. Death-rate spot switching

Requested rule:

> If the current spot causes more than N deaths within a rolling 30-minute window, immediately move to the next spot.

Implement as a rolling timestamp deque, not a periodic counter reset.

```text
on death:
    append death timestamp
    remove timestamps < now - 30 minutes
    if count >= DeathLimit:
        mark spot BAD
        trigger CHANGE_SPOT
```

Default example:

```text
DeathLimit = 10
Window = 30 minutes
```

### Quarantine / BadUntil

Do not immediately rotate back into a dangerous spot.

Example:

```text
10 deaths / 30m
 -> BadUntil = now + 90m
```

The scheduler skips quarantined spots until the cooldown expires unless no other enabled spot exists.

## 8. Loot-efficiency spot switching

The original idea was:

> If a spot does not fill the bag within 30 minutes, switch to another spot.

That rule is technically possible but is a weak proxy for loot quality because stacked items may generate many drops without consuming many slots.

### Better metric hierarchy

Preferred:

```text
LootEventsRolling30m
LootValueRolling30m
NetBagSlotsConsumed
```

Use bag events / fresh bag scans as source of truth.

Potential metrics:

```text
LootRate = loot events / active train minute
LootValueRate = sum(basePrice * quantity delta) / active train minute
BagPressure = FreeBagStart - FreeBagNow
```

`GetFreeBagSpace()` remains useful as a full-bag trigger, but **not as the only measure of spot quality**.

### Simple first version

If value tracking is not implemented yet:

```text
if TrainActive >= 30m
AND LootEventsRolling30m < configured minimum
    -> mark spot low-efficiency
    -> CHANGE_SPOT
```

This is better than “bag not full”.

## 9. Bag full / Auto Sell integration

When bag policy says sell:

```text
remember current spot
 -> stop Train semantically
 -> travel to vendor
 -> open NPC/shop state
 -> scan bag
 -> choose ONE current sell candidate
 -> send semantic sell request
 -> wait RemoveItem / UpdateItemsList / money/shop proof
 -> rescan
 -> repeat until no sell candidates / enough free slots
 -> return to saved spot
 -> verify map/position
 -> resume orchestration
```

Do not use 90 blind sell clicks.

## 10. Spot scheduler: round-robin vs adaptive score

### Simple mode

```text
Spot1 -> Spot2 -> Spot3 -> Spot4 -> Spot1
```

with `BadUntil` skipping dangerous/temporarily disabled spots.

### Recommended adaptive mode

Calculate a score from live metrics.

Conceptual formula:

```text
SpotScore =
    + LootRateWeight * normalizedLootRate
    + LootValueWeight * normalizedLootValue
    + PartyBonus
    - DeathPenalty
    - IdlePenalty
    - TravelPenalty
    - RecentFailurePenalty
```

The exact weights are user policy, not client facts.

The scheduler can remember performance by time bucket, e.g.:

```text
SpotID + day-of-week + hour bucket
```

so the system can learn that one spot is better at a certain time while another is frequently PK-contested.

Do not overfit from one short visit; require a minimum active-train duration before trusting a score.

## 11. State-proof driven transitions

Every transition must have proof.

Examples:

### Travel proof

```text
MapID expected
AND IsMapReady
AND position within tolerance
```

### Party proof

```text
local/target TeamID or C_TeamData changed as expected
```

### Heal proof

```text
fresh HP changed / reached threshold
OR cooldown/progress transition consistent with cast
```

### Sell proof

```text
sold instance removed
OR UpdateItemsList + fresh scan
OR consistent shop/money update
```

### Revive proof

```text
local role alive
AND Revival UI/state cleared
AND map ready
```

Timeouts are failure guards, not proof of success.

## 12. Single-action arbitration

Per PID:

```text
ActionQueue capacity = 1 mutable action
```

Suggested priority:

```text
Captcha/manual pause
 > fatal/error recovery
 > Revival
 > map transition completion
 > critical self survival
 > critical buff emergency
 > Sell transaction currently in progress
 > Party request currently in progress
 > normal Buff
 > Train target/movement
 > background travel/spot optimization
```

Do not interrupt a server-authoritative transaction halfway unless its feature defines a safe cancel path.

## 13. Read-only observers may run concurrently

Safe observers can update snapshots without issuing actions:

```text
NearbyPlayerObserver
BagObserver
MapObserver
Death/RevivalObserver
SkillCooldownObserver
ProgressObserver
CaptchaObserver
TrainSpotMetricsObserver
PartyStateObserver
```

They publish immutable state. The orchestrator consumes snapshots and chooses one next action.

## 14. Multi-client rule

Every PID has a completely independent orchestrator:

```text
PID A -> snapshots/state/action queue/dispatcher/profile A
PID B -> snapshots/state/action queue/dispatcher/profile B
```

Static databases/config tables may be shared read-only.

Persistent user profiles should bind to RoleID/profile identity, not only PID.

## 15. UI proposal

Per client show:

```text
Current state
Current spot
Map / X,Y
Train running/stopped
Party state
Nearby Peace / eligible buff targets
Current buff target
Deaths 30m
Loot events 30m
Loot value 30m
Free bag slots
Current SpotScore
Last action
Last proof/result
```

Train spot editor:

```text
Spot name
Map
X/Y
Tolerance
Train radius
Death limit/window
Loot minimum/window
Quarantine duration
Party behavior
Vendor policy
Enabled
```

Auto Buff filter UI should retain the v1.3.1 scan-and-tick model and per-client profile isolation.

## 16. Failure handling

A spot may fail for many different reasons. Do not collapse all failures into “bad spot”.

Track reason codes such as:

```text
TOO_MANY_DEATHS
LOW_LOOT
TRAVEL_FAILED
MAP_NOT_READY
NO_PATH
PARTY_SPAM_GUARD
VENDOR_FAILED
CAPTCHA
DISPATCHER_NOT_READY
GAME_CLOSED
CLIENT_VERSION_MISMATCH
```

Only performance-related failures should affect long-term SpotScore.

## 17. What should be implemented first

Recommended order:

1. finish validated Unity/MainThread dispatcher;
2. stabilize read-only semantic snapshots per PID;
3. migrate Auto Buff from v1.3.1 behavior donor to semantic scanner + dispatcher;
4. prove one external Peace-player heal end-to-end;
5. implement map travel state proof;
6. implement death rolling window + simple round-robin spot switch;
7. implement bag observer + Auto Sell integration;
8. implement PartyDiscovery/Join using already-mapped team semantics and only targeted runtime validation for any still-unverified join-request payload path;
9. add loot-rate scoring;
10. add adaptive SpotScore after enough telemetry exists.

Do not jump directly to adaptive scoring while action dispatch is still unstable.

## 18. Canonical architecture

```text
Resolver
 -> read-only Scanners / Observers
 -> immutable Snapshot Store
 -> Orchestrator State Machine
 -> Feature Policy (Train/Party/Buff/Sell/Revive/Spot)
 -> Safety Guard
 -> Action Queue (max 1)
 -> Unity/Main Thread Dispatcher
 -> semantic Game/Lua action
 -> state proof
 -> update metrics
 -> next decision
```

## 19. Targeted unknowns only

Do not broad reverse the client for this feature. Remaining exact unknowns should be handled narrowly:

- any still-unverified **join-party request payload/path** needed by the chosen implementation;
- any missing live party-state proof not already exposed by selected/local role data or `C_TeamData`;
- final external `MainThread.Execute -> queue -> Update/DoExecuteWorks` live execution proof;
- server acceptance behavior for specific non-team beneficial skills;
- optional GuildID acquisition path for nearby players without forcing intrusive target mutation.

The leave-team action itself is already VERIFIED: `C_TeamAction.LeaveTeam=4`, payload `4:selfRoleID` through `CMD_TEAM_ACTION`. Do not waste time re-tracing it.

Everything else should first reuse the existing KB.
