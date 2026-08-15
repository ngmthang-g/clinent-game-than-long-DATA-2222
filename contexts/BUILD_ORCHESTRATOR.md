# Context Pack — Build Adaptive Orchestrator

## Scope

Use when one tool coordinates Train, Party, Buff, Revive, Bag/Sell, map travel and spot switching. This pack replaces the temptation to load every feature document separately.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `features/AUTO_ORCHESTRATOR.md`
3. `contexts/BUILD_TOOL_CORE.md`
4. `analysis/22_MAP_MINIMAP_RUNTIME.md`
5. `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`
6. feature pack only for the subsystem currently being implemented.

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

`Captcha/manual pause > fatal recovery > Revival > map transition completion > critical self survival > critical buff > in-progress sell transaction > party transaction > normal buff > train action > optimization/background travel`.

Read-only observers may continue concurrently.

## State-proof rule

Every feature transition needs evidence:

- travel -> expected MapID + `IsMapReady` + position tolerance;
- party -> TeamID/C_TeamData state;
- buff -> fresh HP/cooldown/progress evidence;
- sell -> RemoveItem/UpdateItemsList/shop-money/fresh bag state;
- revive -> local alive + Revival cleared + map ready;
- Train -> semantic mode/target/movement/combat state.

Timeout is a failure guard, not success proof.

## Spot metrics

Maintain per-spot telemetry rather than treating spot as only X/Y:

`MapID, X, Y, tolerance, train radius, deaths rolling window, loot events/value, free bag slots, active train time, idle time, party success, last failure, BadUntil, score`.

## Death-rate switching

Use a rolling timestamp window. Example policy: if deaths in last 30m exceed threshold, quarantine current spot for configured duration and switch.

## Loot-efficiency switching

Prefer loot event/value rate over only “bag became full”. Bag slots are distorted by item stacking.

## Multi-client

Each PID has an independent orchestrator and profile. Shared static databases are read-only only.

## Implementation order

1. stable MainThread bridge;
2. semantic read-only snapshots;
3. individual feature actions with proof;
4. simple orchestrator/round-robin spot switching;
5. telemetry and failure reason codes;
6. adaptive scoring only after stable data exists.

## Completion criteria

No feature runs a competing mutation loop outside the orchestrator action gate; every state transition is observable; failure reasons are explicit; and each client can pause/recover independently without contaminating another PID.