# Context Pack — Build Tool Core

## Scope

Use for architecture, multi-client sessions, state ownership, per-PID isolation, action arbitration, profiles, diagnostics and migration away from legacy remote-worker designs.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/21_MAIN_THREAD_DISPATCHER.md`
3. `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
4. `features/AUTO_ORCHESTRATOR.md`
5. `research/VERIFIED_PHASE3.md`

## OPTIONAL

- `analysis/01_IL2CPP_RUNTIME_METADATA.md` — resolver/metadata details.
- `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md` — behavior/UX donor only.
- `database/AUTO_SETTINGS_SCHEMA.md` — profile/settings serialization.
- `research/TODO.md` — remaining targeted proof items.

## Canonical architecture

`Resolver -> read-only Scanners -> immutable Snapshot Store -> Observer -> Orchestrator/Feature State Machine -> Safety Guard -> Action Queue(max 1 mutable action per PID) -> System.Action -> MainThread.Execute -> semantic action -> state proof`

## Per-PID isolation

Each game process owns its own:

- resolver/runtime handles;
- snapshots;
- current state machine state;
- pending action;
- MainThread Instance/delegate objects;
- cooldown/timer state;
- current target/item/NPC instance IDs;
- settings/profile;
- diagnostics/logs.

Only static readonly databases may be shared.

## VERIFIED contracts

- MainThread queue/Update/dequeue/invoke path is verified.
- Game network producers already use legitimate System.Action -> MainThread.Execute.
- Semantic Lua/Game APIs exist for major gameplay actions.
- UI/server events can provide state proof for many mutations.

## Do not regress to

- `CreateRemoteThread` as production gameplay executor;
- one uncontrolled worker loop issuing actions continuously;
- shared live pointers across clients;
- long prebuilt mutable-action queues;
- fixed sleep as success proof;
- UI screen coordinates as primary identity.

## Core action-gate rule

At most **one mutable action in flight per PID**. Read-only observers may continue updating snapshots.

## Completion criteria

A core build is acceptable only when:

- each PID is isolated;
- mutable action arbitration is centralized;
- action lifecycle has Pending -> Dispatched -> Proof/Timeout -> Complete/Failed;
- dispatcher readiness is explicit;
- map/death/progress/Captcha safety guards are globally available;
- features consume snapshots instead of raw unstable object pointers;
- diagnostics state the exact action and proof/failure reason.