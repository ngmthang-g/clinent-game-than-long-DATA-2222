# Research TODO

This file tracks unanswered questions and planned analysis. Keep tasks evidence-oriented and move conclusions to the appropriate document after verification.

## Phase 1 — Identify the client build

- [ ] Record exact client/game version.
- [ ] Compute SHA-256 for `GameAssembly.dll`.
- [ ] Compute SHA-256 for `global-metadata.dat`.
- [ ] Compute SHA-256 for `UnityPlayer.dll`.
- [ ] Identify Unity version.
- [ ] Identify IL2CPP metadata/runtime version.
- [ ] Inventory native plugins and game-specific modules.

## Phase 2 — Architecture map

- [ ] Map major namespaces/classes from metadata.
- [ ] Identify player/entity representation.
- [ ] Identify NPC representation and RESID mapping.
- [ ] Identify map/position representation.
- [ ] Identify inventory/item model.
- [ ] Identify skill/buff model.
- [ ] Identify UI framework and button event flow.
- [ ] Identify main-thread dispatcher/execution path.

## Phase 3 — Runtime verification

- [ ] Verify player name / RoleID fields.
- [ ] Verify HP / MaxHP fields.
- [ ] Verify world position fields.
- [ ] Verify map identifier/state.
- [ ] Verify nearby entity discovery.
- [ ] Verify NPC identity and coordinates.
- [ ] Verify UI action dispatch behavior.
- [ ] Verify movement/goto behavior.
- [ ] Verify combat/auto mode behavior.
- [ ] Verify revive/reincarnation flow.

## Phase 4 — Feature-oriented research

- [ ] Auto Train specification.
- [ ] Auto Buff specification.
- [ ] Auto Heal specification.
- [ ] Auto Sell specification.
- [ ] Inventory-full detection.
- [ ] Item classification/filtering.
- [ ] NPC selection and nearest-seller logic.
- [ ] Revive/reincarnation action sequence.

## Phase 5 — Knowledge-base hardening

- [ ] Create `analysis/` documents only for researched subsystems.
- [ ] Create `database/` tables for reusable classes/methods/fields/entities.
- [ ] Create `features/` documents for verified end-to-end workflows.
- [ ] Add `PROBABLE`, `HYPOTHESIS`, `FAILED`, and `DEPRECATED` ledgers when first needed.
- [ ] Cross-link every important finding from `AI_INDEX.md`.
- [ ] Ensure every binary-specific conclusion names the client build/hash it applies to.

## Priority rule

Do not spend time rediscovering a fact already marked `VERIFIED` for the same client hashes unless new evidence conflicts with it.
