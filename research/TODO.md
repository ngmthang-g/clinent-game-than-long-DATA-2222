# Research TODO — frozen-client knowledge database

> Main project goal: turn this frozen client into a reusable **AI-readable technical/database corpus** so future tool-building sessions query existing knowledge instead of broad-reversing binaries again.

General architecture, bundle decrypt, Config/Interface extraction, major Lua/UI/runtime semantics, core packet/action discovery and MainThread native internals are DONE.

**Do not broad reverse the client from zero.**

---

# DONE — AI-native navigation / anti-overread layer

- [x] `AI_BOOTSTRAP.md` compact entrypoint.
- [x] `AI_ROUTER.md` task routing.
- [x] task-specific `contexts/BUILD_*.md` packs.
- [x] `database/SUBSYSTEM_SOURCE_MAP.md` subsystem -> source-layer router.
- [x] `database/FINDING_TO_DOC_MAP.md` finding -> canonical doc router.
- [x] `database/FACTS.jsonl` atomic fact index.
- [x] `database/FACTS_README.md` maintenance rules.
- [x] read-budget rule: normal AI task should load only the relevant small context set.

Normal path:

```text
AI_BOOTSTRAP
 -> AI_ROUTER or SUBSYSTEM_SOURCE_MAP
 -> relevant context/canonical docs
 -> exact database lookup
```

---

# DONE — client architecture / semantic discovery

- [x] Unity Windows x64 + IL2CPP, metadata v39.
- [x] GameAssembly/global-metadata semantic mapping.
- [x] LuaSystemManager / SharedData / Game / GUI / Network bridge map.
- [x] `ClickNPC` native internal flow.
- [x] `UIButton.HandleClickEvent` instance/stale-pointer hazard.
- [x] FG custom asset transform/decrypt sufficiently reproduced.
- [x] `Config.unity3d` decoded/extracted: 75 XML tables.
- [x] `Interface.unity3d` decoded/extracted: 338 layouts, 1,469 handler bindings, 339 Lua classes + globals.
- [x] 169 exact `TCPPacketDefine` constants.
- [x] map/NPC/route/FuBen databases.
- [x] exact sell/revive/GameDialog/bag/storage action contracts currently documented.
- [x] built-in Auto Train engine/start semantics.
- [x] nearby peaceful/enemy player structured fields used by shipped UI.
- [x] selected-target rich semantic state.
- [x] skill cooldown / QuickSkill semantics.
- [x] local buff BuffID/DurationTick/Stack.
- [x] bag/shop event lifecycle.
- [x] team/follow schema/action semantics.
- [x] storage/bank semantics.
- [x] ground loot/ItemPack semantic engine.
- [x] Task/Auto Quest donor.
- [x] Pet/Spirit runtime donor.
- [x] Config domain atlas (`analysis/32_CONFIG_DOMAIN_ATLAS.md`).
- [x] underexplored Config normalization plan (`analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`).
- [x] stale Phase-1 assumptions cleaned from master/Lua/world/inventory/combat/asset docs.

---

# DONE — MainThread static/native research

This is retained as client knowledge, but it is **not the main current data-expansion task**.

Verified:

- [x] `MainThread.Awake()` sets singleton Instance.
- [x] `.ctor()` creates `ConcurrentQueue<System.Action>` at `this+0x20`.
- [x] `Execute(Action)` enqueues.
- [x] `Update()` -> `DoExecuteWorks()`.
- [x] `DoExecuteWorks()` dequeues/invokes Actions until empty.
- [x] TCPGame/TCPLogin producers construct legitimate `System.Action` objects and call Execute.
- [x] generated Action constructor ABI recovered.
- [x] relevant IL2CPP allocation/GC/thread/runtime exports identified.

Canonical docs:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`.

Future live bridge proof belongs to implementation work, not broad client research.

---

# P0 — expand the static semantic database

This is the **current main research priority**.

## P0.1 — Skill semantic stack

Build compact indexes + chunked/lossless normalized records for:

- [ ] `Skills` — 2,091 rows.
- [ ] `SkillProperties` — 2,044 rows.
- [ ] `AutoSkills` — 300 rows.
- [ ] `MagicAtrributes` — 509 rows.
- [ ] `Factions` — 17 rows.
- [ ] `Books` — 128 rows.
- [ ] `BookLevelUpCost` — 9 rows.

Desired lookup chain:

```text
SkillID
 -> name/type/faction/target/range/cooldown/property
 -> SkillProperties
 -> MagicAtrributes meanings
 -> faction/book relationships
```

Priority reason: gives future AI a near-direct answer path for Auto Buff/combat/skill questions.

## P0.2 — Item / equipment / medicine stack

- [ ] `Items` — 5,238 rows.
- [ ] `Equips` — 22,763 rows.
- [ ] `Medicines` — 692 rows.
- [ ] `Gems` — 1,154 rows.
- [ ] `EquipSets` — 272 rows.
- [ ] `EquipEnhance` — 99 rows.
- [ ] `EquipIdentifyValues` — 256 rows.
- [ ] `EquipExtendedAttributes` — 29 rows.

Required indexes should support:

```text
ItemID -> identity/type/value/sell/throw rules
EquipID -> Type/EquipPoint/faction/level/star/set/buff/attributes
medicine/gem direct lookup
```

Critical preserved fact:

`Equips.EquipPoint == 0` = Weapon.

## P0.3 — Task / gather / activity stack

- [ ] `Tasks` — 516 rows.
- [ ] `GrowPoints` — 407 rows.
- [ ] `GuildTask` — 360 rows.
- [ ] `Activities` — 45 rows.
- [ ] `DailyActivityAward` — 2 rows.

Goal:

```text
TaskID
 -> type/rule/NPC/monster/item/grow-point/map/dialog/next relationships
```

Unknown positional/extra fields must be preserved rather than discarded.

## P0.4 — Pet / Spirit stack

- [ ] `Pets` — 8,349 rows.
- [ ] `PetFeatures` — 11 rows.
- [ ] `PetEquips` — 70 rows.
- [ ] `PetEquipSets` — 13 rows.
- [ ] `Spirits` — 1,889 rows.
- [ ] `SpiritFeatures` — 3 rows.

Goal:

live Pet/Spirit ID/state -> static template/name/growth/skills/equipment/feature semantics.

### Storage design

Large tables must use small indexes plus chunks, e.g.:

```text
database/static/skills/SKILL_INDEX.csv
database/static/skills/SKILLS_0001_0500.csv
...
```

Do **not** make AI read a single giant Markdown/CSV when it only needs one ID.

### Current repository-state truth

Schemas/counts and substantial derived knowledge are already in GitHub, but the full normalized row chunks for the biggest tables are **not yet present under `database/static/...`**.

Do not tell future AI those files exist until they actually appear in the tree.

---

# P1 — semantic indexes from other already-decoded bundles

## P1.1 — Translations

- [ ] inventory TextAsset/string-table structure from decoded `Translations.unity3d`.
- [ ] if useful, create localization key -> text/language index.
- [ ] connect localized labels to dialog/service/UI matching.

Potential value:

robust matching of visible server/UI text without hardcoding one wording.

Do not guess the internal schema before extraction.

## P1.2 — shared Interface resources

Only if needed by a concrete question:

- [ ] inventory `Shared.unity3d` / `Shared_2.unity3d` asset names/types.
- [ ] map relevant prefab/resource IDs.

Lua/layout remains the preferred UI semantic source.

## P1.3 — `data.unity3d`

Large (~47.6 MB), plain UnityFS.

Do not broad-extract it pre-emptively.

If a concrete gap appears:

- [ ] build an asset inventory first;
- [ ] isolate relevant map/path/scene/resource objects;
- [ ] extract only useful semantic structures;
- [ ] commit an index/result rather than raw noise.

---

# P1 — runtime-only targeted proofs

These cannot be resolved by writing more static prose.

## NPC Trị liệu

- [ ] capture active server `GameDialog.Selections` at intended healer.
- [ ] identify actual visible treatment selection/text.
- [ ] record current selectionID and any confirmation step.
- [ ] prove HP/money/dialog outcome.

Static NPC 339 = Đỗ Thanh Đằng / LangZhong1 / Lâu Lan is VERIFIED; service selection remains runtime/server-driven.

## Non-team beneficial skill acceptance

- [ ] verify which support skills can target a non-team PeacePlayer.
- [ ] record range/relationship/server restrictions.
- [ ] prove success from HP/buff/cooldown/progress state.

## Additional actor fields

Only when a feature actually needs them:

- [ ] exact Position/death/social/combat fields beyond shipped nearby UI schema.
- [ ] richer target-buff IDs/durations if target icons are insufficient.
- [ ] exact special NPC/Monster/Pet/GrowPoint object fields not already exposed semantically.

---

# P2 — analytics / optional deeper models

## Combat telemetry

- [ ] map exact `CMD_SKILL_DAMAGE` / `CMD_SKILL_HEAL` / death/buff event payloads.
- [ ] determine attacker/target/SkillID/value/timing fields.
- [ ] investigate crit/elemental/XP/loot linkage only if evidence supports it.

## Offline route planner

- [ ] use 165 portal + 506 NPC-mediated edges for adjacency/diagnostics.
- [ ] model level/quest/event restrictions if needed.
- [ ] keep runtime `Game.GoTo` as preferred executor.

## PathFinder / NodeGrid

- [ ] only inspect if stock runtime pathing becomes an actual blocker.
- [ ] avoid expensive path/grid extraction without a concrete use case.

---

# P2 — low-priority client branches

Only investigate if directly requested:

- Launcher sync/record-playback internals.
- `SyncBootstrap.AutoInit` meaning.
- LiveKit/voice internals.
- Burst jobs.
- UnityPlayer engine internals.
- graphics/baselib/crash-handler internals.

These are not current gameplay-knowledge priorities.

---

# Knowledge hygiene — ongoing

For every meaningful discovery:

```text
raw evidence
 -> interpretation
 -> canonical subsystem doc
 -> database/index if appropriate
 -> VERIFIED/PROBABLE/HYPOTHESIS ledger
 -> routing cross-link if useful
```

Rules:

- promote solved predictions out of PROBABLE/HYPOTHESES;
- never invent missing rows/fields;
- preserve unknown Config columns/nested data during normalization;
- keep static template data separate from runtime server-authoritative state;
- packet symbol != exact request payload;
- response handler != request action;
- no invented NPC coordinates when `Game.GetNPCPosition` exists;
- no invented treatment selection IDs;
- no automatic Captcha solving/bypass.
