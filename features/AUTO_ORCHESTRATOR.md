# Feature specification — Adaptive Auto Orchestrator

Status: **DESIGN SYNTHESIS** from VERIFIED client state/action contracts. The full orchestrator is tool design, not a shipped game feature.

Purpose: coordinate Auto Train, Party, Auto Buff, Revive, Auto Sell, travel and train-spot switching as **one state machine per PID** without competing mutable-action loops.

Read first:

- `AUTO_FEATURE_READINESS.md`
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md`

---

# 1. Core architecture

Per client:

```text
Resolver
 -> read-only Scanners / Observers
 -> immutable Snapshot Store
 -> Orchestrator State Machine
 -> Feature Policy
 -> Safety Guard
 -> Action Gate (max 1 mutable action)
 -> Unity/MainThread dispatcher
 -> semantic Game/Lua/UI action
 -> concrete state proof
 -> fresh snapshot
 -> next decision
```

Read-only observers may run concurrently. Mutable actions may not.

Every PID owns independent live state. Static Config/database data may be shared read-only.

---

# 2. Canonical top-level states

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
RETURN_TO_SPOT
SPOT_EVALUATION
CHANGE_SPOT
PAUSED_CAPTCHA
RECOVERY
ERROR
```

A feature may have inner states, but all mutations still pass through the single per-PID action gate.

---

# 3. Per-PID snapshots

Use `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md` as the canonical schema.

Important publications:

```text
LocalRoleSnapshot
MapSnapshot
NearbyPeacePlayers
NearbyTrainTargets
SelectedTargetSnapshot
BagSnapshot
BuffSnapshot
SkillCooldownSnapshot
TeamSnapshot
GameDialogSnapshot
ShopTransactionSnapshot
RevivalSnapshot
```

Every snapshot/action candidate carries freshness/version information. A tool-owned `WorldGeneration` invalidates stale world/UI transaction state after map/loading generations change.

Never retain Lua/C#/UIButton/item object pointers as long-lived external identity.

---

# 4. One-action arbitration

Recommended priority:

```text
CAPTCHA / MANUAL PAUSE
 > fatal/error recovery
 > REVIVAL
 > map-transition completion
 > critical self survival
 > critical Buff/Heal
 > current Sell/NPC transaction
 > current Party transaction
 > normal Buff
 > Train target/chase/cast
 > Loot
 > background spot/travel optimization
```

Do not interrupt a server-authoritative transaction halfway unless its feature has a proven safe cancel path.

---

# 5. State-proof rule

Every transition needs evidence.

Travel:

```text
expected MapID
AND Game.IsMapReady()
AND valid fresh position
AND distance(position,destination) <= tolerance
```

Party:

```text
Game.RoleData.TeamID / C_TeamData changed as expected
```

Buff/heal:

```text
fresh target HP change
OR buff/icon evidence when available
OR cooldown/progress transition consistent with cast
```

Sell:

```text
sold instance removed
OR UpdateItemsList + fresh BagSnapshot
OR consistent shop/money update
```

Revive:

```text
local role alive
AND Revival state cleared
AND map ready
AND valid position
```

Timeout means failure/unknown, never success.

---

# 6. Train spot profile

A spot should be a first-class record:

```text
SpotID
Name
MapID
TrainX
TrainY
Tolerance
TrainRadius
PreferredVendor / VendorPolicy
PartyPolicy
Enabled
Priority
BadUntil
```

Useful runtime metrics:

```text
VisitStartedAt
DeathsRollingWindow
LootEventsRollingWindow
LootValueRollingWindow optional
FreeBagStart
FreeBagNow
ActiveTrainSeconds
IdleNoTargetSeconds
PartyJoinAttempts
PartyJoinSuccess
TravelFailures
LastFailureReason
LastVisitedAt
SpotScore optional
```

---

# 7. Cross-map travel / return-to-spot

Canonical pattern:

```text
StartAutoFight(None)
 -> wait Train ownership yielded
 -> Game.GoTo(MapID,X,Y)
 -> wait expected MapID
 -> wait IsMapReady
 -> wait valid position
 -> wait distance <= tolerance
 -> continue
```

Use `GetCurrentMoveDestination()` for movement diagnostics when needed.

Do not use a fixed post-map delay as the state transition.

---

# 8. Party behavior — exact requests already solved

Candidate discovery can use nearby peaceful players / nearby team-leader semantics as appropriate.

## Leave current team

```text
CMD_TEAM_ACTION
C_TeamAction.LeaveTeam = 4
payload = 4:selfRoleID
```

## Request to join selected target's team

Verified from shipped `OtherRolePopup.lua`:

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamRequestJoin = 9
payload = 9:targetRoleID
```

## Invite selected target to local team

```text
CMD_OTHER_ROLE_COMMAND = 200051
C_OtherRoleCommand.TeamInviter = 5
payload = 5:targetRoleID
```

Do **not** confuse `C_TeamAction.RequestJoin=7` with `C_OtherRoleCommand.TeamRequestJoin=9`; they belong to different action families.

Automatic join flow:

```text
arrive spot
 -> optional leave old/incompatible team
 -> fresh candidate RoleID
 -> send ONE 200051 / 9:RoleID
 -> wait TeamID/C_TeamData proof
 -> accepted: continue
 -> rejected/timeout: cooldown candidate
 -> optionally try next
```

Never request every visible player continuously.

**Join-party request construction is not a remaining reverse-engineering gap.**

---

# 9. Auto Train ownership

Exact semantic mode:

```text
C_AutoModel.Train = 1
```

Start:

```text
GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)
```

Stop/yield:

```text
StartAutoFight(C_AutoModel.None)
```

The visible `Đánh quái` settings tab is not the semantic start action.

Before Sell, explicit NPC travel or spot switching, stop/yield Train so combat movement does not compete with the higher-level state.

---

# 10. Auto Buff arbitration

Candidate source:

`Game.GetNearByPeacePlayers(limit)`.

Verified fields:

```text
RoleID, Name, Level, FactionID,
HP, MaxHP, GuildName, AvartaID, TeamRank
```

Possible filters:

```text
RoleID/name whitelist
guild
faction
level range
MaxHP range
HP threshold
include/exclude self
```

Every cast:

```text
fresh candidate
 -> revalidate HP/identity
 -> skill ownership/condition/cooldown
 -> range/chase
 -> ONE RequestUsingSkillWithTarget
 -> wait proof
 -> rescan
```

Important remaining runtime boundary: server acceptance for intended beneficial skills on non-team PeacePlayers must be proven per intended skill/relationship.

---

# 11. Bag / Auto Sell arbitration

Trigger from semantic bag state:

`Game.GetFreeBagSpace()`.

Use `database/AUTO_SELL_CLASSIFICATION.md` for compact policy.

Sell transaction:

```text
remember current spot/mode
 -> stop Train
 -> route to configured vendor
 -> wait actual NPCShop state
 -> fresh BagSnapshot
 -> choose ONE current instance
 -> CMD_NPC_SHOP_SELL_REQUEST 200036
 -> wait removal/update proof
 -> rescan
 -> repeat
 -> return to saved spot
 -> verify arrival
 -> resume Train
```

Do not use 90 blind sell clicks.

Vendor-service mapping remains runtime-promoted: static NPC identity/ResName alone does not prove an NPC opens the desired sell-capable shop.

---

# 12. Revive ownership

Exact packet:

```text
CMD_REVIVE_DATA = 200063
1 = normal / Đầu thai
2 = newbie
3 = skill revive
```

Revive preempts Train/Buff/Sell except manual Captcha pause.

Flow:

```text
dead / Revival active
 -> remember prior spot/mode
 -> send one allowed revive action
 -> wait alive + Revival cleared + map ready
 -> optional return to saved spot
 -> verify position
 -> resume prior mode
```

---

# 13. NPC treatment ownership

```text
stop conflicting Train movement
 -> GoToNPC / GetNPCPosition
 -> wait current GameDialog
 -> inspect current Selections[selectionID]=visibleText
 -> match treatment text
 -> submit actual selectionID
 -> wait HP/money/dialog proof
 -> return/resume
```

Do not hardcode a global Trị liệu selection ID.

NPC 339 Đỗ Thanh Đằng / Lâu Lan is a strong static healer candidate; exact live treatment sequence remains targeted runtime evidence.

---

# 14. Death-rate spot switching

Use a rolling timestamp deque, not a counter reset on clock boundaries.

```text
on death:
  append timestamp
  remove timestamps older than configured window
  if count >= DeathLimit:
      currentSpot.BadUntil = now + quarantineDuration
      CHANGE_SPOT
```

This prevents immediately rotating back into a dangerous spot.

---

# 15. Loot-efficiency spot switching

“Bag not full after N minutes” is a weak proxy because stackable items distort bag pressure.

Preferred metrics:

```text
LootEvents / ActiveTrainMinute
LootValue / ActiveTrainMinute optional
NetBagSlotsConsumed
IdleNoTargetSeconds
```

Start simple. Do not add adaptive scoring until basic action/state reliability is proven.

---

# 16. Spot selection

Simple mode: round-robin enabled spots while skipping `BadUntil` spots.

Later adaptive score may use:

```text
+ loot rate/value
+ party availability
- death rate
- idle/no-target rate
- travel failure rate
- recent failure penalty
```

Weights are tool/user policy, not client facts.

---

# 17. Failure reason taxonomy

Useful external reason codes:

```text
STALE_SNAPSHOT
ACTION_GATE_BUSY
MAP_NOT_READY
ROLE_DEAD
CAPTCHA_PAUSE
PROGRESS_BLOCKED
TARGET_GONE
TARGET_DEAD
NO_PATH
SKILL_NOT_READY
SKILL_NO_PROOF
NPC_NOT_FOUND
DIALOG_NOT_READY
DIALOG_SELECTION_NOT_FOUND
SHOP_NOT_READY
ITEM_GONE
ITEM_NOT_SELLABLE
SELL_NO_PROOF
PARTY_REQUEST_TIMEOUT
TRAVEL_TIMEOUT
REVIVE_NO_PROOF
CLIENT_GONE
DISPATCHER_NOT_READY
```

Do not collapse all failures into one “auto failed” state.

---

# 18. Multi-client rule

Per PID:

```text
Resolver
Snapshot versions / WorldGeneration
Feature state
Action gate
Dispatcher state
Spot profile
User settings
Metrics
Last action
Last proof/result
```

Never share live client pointers/state across PIDs.

Persistent profiles should preferably bind to character RoleID/profile identity rather than PID alone.

---

# 19. Implementation order

Recommended order:

1. external managed Action -> MainThread live proof;
2. stable semantic per-PID snapshots;
3. Auto Train start/stop + state proof;
4. Auto Buff semantic cast + one non-team acceptance proof if used;
5. map travel/return proof;
6. Revive recovery;
7. bag observer + Auto Sell transaction;
8. Party join/leave using already-recovered exact requests;
9. simple rolling-death spot switching;
10. loot-rate metrics;
11. adaptive scoring only after enough stable telemetry exists.

---

# 20. Remaining knowledge gaps — narrow only

Current gaps that can materially affect the orchestrator:

1. live external `System.Action -> MainThread.Execute` proof;
2. non-team beneficial-skill server acceptance for the exact skills used;
3. exact live Trị liệu dialog sequence/outcome for chosen healer;
4. specific vendor-service promotion for configured Train maps/NPCs where shop service is not yet runtime-proven;
5. additional actor fields only if a concrete feature cannot operate from current snapshots.

**Not a gap:** join-party request construction. It is already VERIFIED as `CMD_OTHER_ROLE_COMMAND=200051`, payload `9:targetRoleID`.

Do not broad reverse unrelated client systems to expand this list.