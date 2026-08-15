# AI Knowledge Index

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`
Default branch: `main`
Purpose: canonical knowledge base for analysis of the Than Long game client.

## Read this first

Any AI or developer working with this repository should read this file before re-analyzing client binaries.

Rules:

1. Prefer existing `VERIFIED` knowledge over repeating analysis.
2. Treat `PROBABLE` and `HYPOTHESIS` findings as unverified until runtime or binary evidence confirms them.
3. Re-check binary-dependent facts when client hashes change.
4. Do not silently promote assumptions to facts.
5. Record failed approaches so later work does not repeat them.
6. Keep evidence paths, relevant class/method/field names, and client version/hash with every important finding.

## Source-of-truth hierarchy

1. Original client binaries and data under `Game/` and repository root.
2. `CLIENT_MANIFEST.md` for client identity and hash/version tracking.
3. `research/VERIFIED.md` for confirmed findings.
4. Topic documents under `analysis/`, `database/`, and `features/` when created.
5. `research/TODO.md` for unanswered questions and planned investigations.

## Status vocabulary

- `VERIFIED` — confirmed by direct binary/runtime evidence or repeatable test.
- `PROBABLE` — strong evidence, but not yet runtime-confirmed.
- `HYPOTHESIS` — plausible interpretation requiring validation.
- `FAILED` — tested approach did not work or produced unreliable results.
- `DEPRECATED` — previously valid information that no longer applies to the current client.

## Planned knowledge areas

### Architecture
- Unity / IL2CPP structure
- native modules and plugins
- metadata/runtime relationships
- main-thread execution model

### Game data
- player/entity model
- HP / MaxHP / role identity
- position and map state
- NPCs and RESIDs
- items and inventory
- skills and buffs
- UI buttons and dialogs

### Automation-relevant systems
- movement / goto
- combat / auto-train
- revive / reincarnation flow
- NPC interaction
- inventory checking and selling
- healing
- buff logic

## Planned document map

`analysis/`
- architecture and subsystem explanations

`database/`
- reusable class/method/field/entity references

`features/`
- end-to-end feature specifications and verified action sequences

`research/`
- verification state, open questions, and failed approaches

## Current state

Knowledge-base foundation created. Deep binary analysis has not yet been recorded here. Before adding technical conclusions, populate `CLIENT_MANIFEST.md` with hashes for the exact client build being studied.
