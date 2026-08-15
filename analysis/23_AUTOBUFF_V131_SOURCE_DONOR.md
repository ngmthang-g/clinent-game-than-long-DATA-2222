# Source donor audit — ThanLong Auto Buff v1.3.1

Status: **SOURCE-INSPECTED DONOR**, not a replacement for the canonical VERIFIED runtime model.

Source package inspected: `ThanLongAutoBuff_Source_v1.3.1(1).zip`.

- ZIP SHA-256: `4dedc55a9df08abd69632c79d67827cc8d5730272c7b9fe5f82551d7ce76ace4`
- `src/main.cpp`: `8e5495989af68256ab122fb197ee9a4366c62c6f15cdbebf5f49017ef4872a20`
- `src/game_session_v12.inc`: `a6eac551582c6a2e93683ceab5498354594d1c5717b258be97f8c19b9ff663d6`
- `src/ui_v12.inc`: `39c48cd4a7bb924010d32401c59bbb25c3493f16214a9622dc2a723a40f0dbd9`
- `src/remote_worker.S`: `b58c3c422c185965bf91723366be3e826ca3002f863f5cb396aac67100a849e1`
- packaged EXE SHA-256 from source bundle: `38e7cac144a7692606eeb621b68e877b80facff3e7b80a0f63349f86d97e0cef`

The package declares the same frozen client fingerprints already used by the project for `GameAssembly.dll` and `global-metadata.dat`.

## 1. Why this source is valuable

This source is useful mainly as a **behavior / UX / state-policy donor**. It contains several ideas that should be preserved in the new architecture even though its low-level execution mechanism should not be copied.

The strongest reusable ideas are:

1. one independent session per game PID;
2. per-character/per-window configuration and profile isolation;
3. dynamic scan-and-tick filters instead of free-text filters;
4. RoleID as the stable identity for selected characters;
5. faction filtering by FactionID instead of display text alone;
6. explicit self-buff branch separate from nearby-player scanning;
7. HP threshold + level + MaxHP range + guild + faction + RoleID filters composed together;
8. multiple priority policies, including target lock for MaxHP-based healing;
9. revalidation of the target immediately before a mutable cast;
10. skill discovery from the current character rather than assuming every account owns the same skills;
11. live counters and per-session status for debugging/observability;
12. short retry TTL for temporarily missing names/guild/faction rather than caching blank data indefinitely;
13. profile persistence that only reports success after the OS confirms the write;
14. automatic reconnect/reinitialize when the call channel fails;
15. build/version gating before invoking game methods.

These are good product/engine patterns and should survive the migration to the semantic scanner + main-thread action architecture.

## 2. Source architecture observed

The source implements a `GameSession` per PID. Each session owns:

- process handle;
- game module information;
- worker thread;
- runtime call executor;
- independent `AutoConfig`;
- independent skill list;
- filter state;
- scan statistics;
- target anti-spam state;
- cache for name/guild/faction;
- last target / command count;
- target lock state for MaxHP priority.

This is directionally correct for multi-client design: **state may be shared as immutable static config/database, but live pointers, target state, action state and dispatcher context must never be shared across PIDs.**

## 3. Filter model worth keeping

The source config combines:

```text
HP threshold
include self
SkillID / SkillName
priority mode
guild selection
faction selection
RoleID selection
minimum level
maximum level
minimum MaxHP
maximum MaxHP
```

The scan-and-tick UI is especially useful:

- nearby Peace players are scanned;
- guild options are built from observed guild names;
- faction options are keyed by FactionID;
- player options are keyed by RoleID;
- selected entries remain configured even if they later disappear from AOI.

This is better than free-text-only configuration because it reduces spelling errors and makes RoleID the canonical identity.

### Recommended canonical filter semantics

Use an immutable candidate snapshot:

```text
RoleID
Name
Level
FactionID
FactionName
GuildName
HP
MaxHP
HPPercent
TeamRank
Position if available
LastSeenTick
```

Then apply filters in deterministic order:

```text
Peace/alive eligibility
 -> explicit RoleID selection
 -> guild
 -> faction
 -> level range
 -> MaxHP range
 -> HP threshold
 -> priority policy
```

The current canonical source should obtain this data through `Game.GetNearByPeacePlayers(MaxPlayers)` and related semantic target data rather than directly walking `ObjectManager.sprites`.

## 4. Priority policies from v1.3.1

The source implements three modes:

1. lowest HP percent first;
2. highest MaxHP first;
3. lowest MaxHP first.

For MaxHP modes it keeps `lockedPriorityTargetID_`: once a target is chosen, that target remains preferred until it no longer qualifies. This matches the requested behavior of healing the highest-MaxHP eligible player to the configured threshold before moving to the next one.

### Improvement: emergency preemption

Pure target lock can starve a critical player while the locked player is still below a relatively high threshold. Recommended optional policy:

```text
normal target = locked MaxHP-priority target
BUT
if another eligible target HPPercent <= CriticalHPPercent
    temporarily preempt lock and heal the critical target
then return to the locked target if still eligible
```

Example UI:

```text
Priority: MaxHP cao nhất
Heal threshold: 70%
Emergency override: 25%
```

This preserves deterministic MaxHP priority without ignoring a nearby player at 5–10% HP.

## 5. Revalidation before cast is a strong donor pattern

The source does not trust the first scan all the way to the cast. Immediately before `RequestUsingSkillWithTarget` it re-reads/re-checks:

- HP and MaxHP;
- HP threshold;
- Peace relationship for other players;
- latest live configuration;
- RoleID/guild/faction/level/MaxHP filters;
- character can-use-skill state;
- cooldown state;
- skill condition.

This pattern should be preserved, but with canonical APIs and main-thread action dispatch.

Recommended flow:

```text
read-only snapshot
 -> choose candidate
 -> acquire single mutable-action slot
 -> re-read target by RoleID
 -> revalidate all safety/eligibility rules
 -> ensure range/path/cooldown/progress state
 -> dispatch one semantic cast on Unity main thread
 -> observe state proof
 -> release slot
 -> rescan
```

## 6. Anti-spam / pacing donor

The source uses:

- 2.5 s per-target cast suppression;
- minimum 700 ms between any two cast requests.

These are useful **prototype guards**, but they should not become fixed truth. The canonical engine now knows exact skill ProgressTime and cooldown semantics, so timing should be derived from skill/runtime state first; fixed intervals should only be secondary rate-limit guards.

## 7. Cache strategy worth preserving

The source uses asymmetric cache TTLs:

- valid name: about 5 minutes; fallback/empty result: about 2 seconds;
- valid guild: about 15 seconds; empty result: about 2 seconds;
- valid faction name: about 30 minutes; empty result: about 2 seconds.

The key lesson is important: **never cache transient failure as stable absence**.

Recommended canonical cache:

```text
RoleID -> stable display name cache
FactionID -> static/long-lived faction name cache
RoleID -> guild metadata cache with shorter TTL
empty/error -> very short TTL
```

Where possible, IDs should be persisted and names treated as display metadata.

## 8. Skill discovery / profile donor

The source reads the current character's skill dictionary, resolves names, checks ownership, and allows a per-session skill choice. If automatic mode is selected it prefers Thanh Tâm Phổ Thiện Chú by normalized name.

Canonical improvements:

- prefer verified static SkillID identity (`424` for Thanh Tâm Phổ Thiện Chú) over fuzzy-name identity;
- still enumerate owned skills for UI and account-specific availability;
- validate `Game.HasSkill(skillID)` and cooldown/condition before cast;
- expose the actual semantic name + SkillID in the UI;
- never trust the legacy misleading `KIMCHAMDOKIEP=407` variable name.

## 9. Observability donor

The source exposes per-session counters:

- detected nearby roles;
- Peace roles;
- matched filters;
- low-HP eligible targets;
- hostile count;
- commands sent;
- last target;
- running/stopped status.

This is extremely useful for diagnosing why an automation appears idle.

Recommended future per-client diagnostics:

```text
Scanner:
  nearbyPeace
  matchedFilter
  lowHP
  targetSelected

Action:
  currentState
  currentAction
  actionQueueDepth (0/1)
  lastActionResult
  lastStateProof

Safety:
  mapReady
  captcha
  dead/revival
  progressActive
  dispatcherReady

Feature counters:
  healsAccepted/proven
  healsRequested
  deaths30m
  lootEvents30m
  freeBagSlots
  currentTrainSpot
  spotScore
```

Do not label `commandsSent` as successful healing. The source's own audit correctly notes that a request invocation does not prove server acceptance or HP increase.

## 10. Parts of v1.3.1 that must NOT be copied

### 10.1 `CreateRemoteThread` / `remote_worker.S`

The source allocates executable memory in the game, injects a position-independent worker, starts it with `CreateRemoteThread`, attaches that thread to IL2CPP, then calls arbitrary game methods from that remote worker.

This conflicts with the canonical architecture and is a likely stability risk for mutable Unity/Lua/Game actions.

**Rule:** keep this only as historical donor evidence. Do not use `RemoteExecutor` / `remote_worker.S` for new mutable actions.

Target architecture remains:

```text
Resolver
 -> read-only Scanner
 -> Snapshot/State Store
 -> Observer
 -> State Machine
 -> Safety Guard
 -> Action Queue (max 1)
 -> validated Unity/Main Thread Dispatcher
 -> semantic Game/Lua action
 -> state proof
```

### 10.2 Hardcoded RVA/offset as primary identity

The source hardcodes many RVAs and object offsets and protects them with PE timestamp, image size and 19 byte signatures. The signature gate is a useful fail-closed safety idea, but the new implementation should resolve by semantic metadata/API identity first.

Historic RVA/signature may remain as optional diagnostics for the frozen snapshot, not the sole source of truth.

### 10.3 Direct `ObjectManager.sprites` enumeration

The source manually walks a dictionary and checks class pointer equality to identify `GRole`. Current KB has the stronger shipped semantic API:

`Game.GetNearByPeacePlayers(MaxPlayers)`.

Use the semantic list first. Direct object enumeration is a fallback/debug donor only.

### 10.4 Missing Unity main-thread proof

`CanUseSkill`, cooldown and condition checks are not enough to make a mutable call thread-safe. `RequestUsingSkillWithTarget` must be dispatched through the validated game-owned main-thread mechanism.

### 10.5 No range/chase handling in the cast loop

The source sends the target-skill request after eligibility checks but does not implement the built-in donor's exact range/chase flow.

Canonical behavior should use:

```text
GetSkillLuaData(skillID)
 -> CastRange
 -> GetDistance
 -> CellToDistance
 -> ChaseTarget if needed
 -> RequestUsingSkillWithTarget
```

### 10.6 Dead targets are filtered out by `ReadVitals`

The source requires `hp > 0`, so dead nearby players cannot become candidates. That is acceptable for a heal-only prototype but blocks resurrection logic.

A future Nga My support engine should model:

```text
AliveLowHP -> heal policy
DeadEligible -> Khởi Tử Hồi Sinh (408) policy
```

with separate cooldown/range/progress rules.

### 10.7 Incomplete global safety state

The source does not model the complete canonical guards now known from the client:

- Captcha;
- map loading / `IsMapReady`;
- Revival/death state;
- channel/progress state;
- state-proof after server-authoritative actions.

These guards must wrap the old donor logic before production integration.

## 11. Multi-client implementation rule derived from the source

The source's strongest architectural success is isolation by PID. Preserve it, but bind persistent identity to character data rather than PID alone because PID changes after restart.

Recommended persistent key:

```text
CharacterProfileKey = account/profile choice + RoleID
```

Runtime session key:

```text
ProcessSessionKey = PID + current RoleID
```

Each session owns its own:

- resolver context;
- scanner snapshot;
- selected RoleIDs/guild/faction filters;
- skill profile;
- target lock;
- cooldown observer;
- action queue;
- dispatcher context;
- Auto Train/Auto Sell/Revive/Party state;
- diagnostics.

## 12. How this donor connects to the larger automation design

The v1.3.1 source supplies a mature **target-filter / priority / profile / multi-client UI model**. The canonical KB supplies the safer semantic scanner/action APIs. The new automation should combine them rather than choosing one wholesale.

Recommended synthesis:

```text
v1.3.1 UX/policy donor
    +
semantic nearby/player APIs
    +
verified skill/buff/cooldown data
    +
main-thread dispatcher
    +
single-action state machine
    =
new stable Auto Buff core
```

That core can then plug into the higher-level Auto Orchestrator described in `features/AUTO_ORCHESTRATOR.md`.

## 13. Runtime proof still required

Before declaring the migrated Auto Buff fully VERIFIED:

1. prove `GetNearByPeacePlayers` through the live bridge;
2. prove exact returned field access in the new scanner;
3. finish Unity/main-thread dispatcher proof;
4. cast 424 on a non-team Peace RoleID through the dispatcher;
5. confirm HP/state change or another server-side proof;
6. test range/chase behavior;
7. test target disappearance/map transition mid-cast;
8. test multi-client isolation with at least two game processes;
9. test Captcha/loading/death/progress guards;
10. record outcomes in VERIFIED/TODO rather than assuming source implementation equals runtime proof.
