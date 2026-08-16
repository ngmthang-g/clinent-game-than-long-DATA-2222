# Context Pack — Build Adaptive Orchestrator

## Scope

Use when one tool coordinates Train, Party, Buff, Revive, Bag/Sell, map travel and spot switching. This pack replaces the temptation to load every feature document separately.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `AUTO_FEATURE_READINESS.md`
4. `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`
5. `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md`
6. `features/AUTO_ORCHESTRATOR.md`
7. feature pack only for the subsystem currently being implemented.

## Feature packs to open on demand

- Train -> `contexts/BUILD_AUTO_TRAIN.md`
- Buff -> `contexts/BUILD_AUTO_BUFF.md`
- Sell -> `contexts/BUILD_AUTO_SELL.md`
- Revive -> `contexts/BUILD_AUTO_REVIVE.md`
- Party -> `contexts/BUILD_PARTY.md`
- NPC treatment -> `contexts/BUILD_AUTO_HEAL.md`
- MainThread bridge -> `contexts/BUILD_MAINTHREAD_BRIDGE.md`

Do not preload them all unless designing a cross-feature interface contract.

## Canonical top-level states

Recommended family:

`IDLE, PRECHECK, TRAVEL_TO_SPOT, WAIT_MAP_READY, PARTY_DISCOVERY, PARTY_REQUEST, START_TRAIN, TRAINING, BUFF_SUPPORT, REVIVAL, BAG_EVALUATION, SELLING, RETURN_TO_SPOT, SPOT_EVALUATION, CHANGE_SPOT, PAUSED_CAPTCHA, RECOVERY, ERROR`.

## One-action arbitration

Per PID, at most one mutable action in flight.

Suggested priority:

`Captcha/manual pause > fatal recovery > Revival > map transition completion > critical self survival > critical buff > in-progress sell transaction > party transaction > normal buff > train action > loot > optimization/background travel`.

Read-only observers may continue concurrently and publish immutable snapshots.

## State-proof rule

Every feature transition needs evidence:

- travel -> expected MapID + `IsMapReady` + position tolerance;
- party -> `Game.RoleData.TeamID` / `C_TeamData` state;
- buff -> fresh HP/cooldown/progress evidence;
- sell -> RemoveItem/UpdateItemsList/shop-money/fresh bag state;
- revive -> local alive + Revival cleared + map ready;
- Train -> semantic mode/target/movement/combat state.

Timeout is a failure guard, not success proof.

## Party actions already solved

Do not broad-trace these again:

```text
Leave current team:
  CMD_TEAM_ACTION
  payload = 4:selfRoleID

Request to join selected target's team:
  CMD_OTHER_ROLE_COMMAND = 200051
  C_OtherRoleCommand.TeamRequestJoin = 9
  payload = 9:targetRoleID

Invite selected target to local team:
  CMD_OTHER_ROLE_COMMAND = 200051
  C_OtherRoleCommand.TeamInviter = 5
  payload = 5:targetRoleID
```

After any request, membership success still requires fresh TeamID/C_TeamData proof. Request sent is not acceptance.

Use anti-spam cooldowns per target RoleID.

## Spot metrics

Maintain per-spot telemetry rather than treating spot as only X/Y:

`MapID, X, Y, tolerance, train radius, deaths rolling window, loot events/value, free bag slots, active train time, idle time, party success, last failure, BadUntil, score`.

## Death-rate switching

Use a rolling timestamp window. Example policy: if deaths in last 30m exceed threshold, quarantine current spot for configured duration and switch.

## Loot-efficiency switching

Prefer loot event/value rate over only “bag became full”. Bag slots are distorted by item stacking.

## Multi-client

Each PID has an independent:

```text
SnapshotVersion / WorldGeneration
Local/nearby/bag/team/dialog/shop snapshots
Feature state machines
Action gate
Dispatcher state
Profile
Metrics
Last action/result
```

Shared static databases are read-only only.

## Implementation order

1. stable MainThread bridge;
2. semantic read-only snapshots using `analysis/35...`;
3. individual feature actions with proof;
4. simple orchestrator/round-robin spot switching;
5. party join/leave using already-solved semantic requests;
6. telemetry and failure reason codes;
7. adaptive scoring only after stable data exists.

## Remaining research gaps relevant to the orchestrator

Do not invent new gaps. Current important unresolved items are narrow:

- external managed `System.Action -> MainThread.Execute` live bridge proof;
- server acceptance of intended non-team beneficial skill(s);
- exact runtime Trị liệu dialog sequence for chosen healer;
- specific vendor-service promotion only for configured Auto Sell maps/NPCs if not already proven;
- additional actor fields only when a concrete feature cannot work from current snapshots.

**Party join request construction is already solved.**

## Completion criteria

No feature runs a competing mutation loop outside the orchestrator action gate; every state transition is observable; failure reasons are explicit; every live object is revalidated from fresh per-PID snapshots; and each client can pause/recover independently without contaminating another PID.