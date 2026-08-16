# Research TODO — automation-tool-focused knowledge base

> Main goal: turn this frozen client into a reusable **AI-readable knowledge base for building the Thần Long auto tool**. Do not expand unrelated client knowledge unless it materially improves an automation feature.

Read `AUTO_TOOL_SCOPE.md` and `AUTO_FEATURE_READINESS.md` before adding new research.

General architecture, bundle decrypt, Config/Interface extraction, major Lua/UI/runtime semantics, core packet/action discovery and MainThread native internals are DONE.

**Do not broad reverse the client from zero.**

---

# DONE — auto-tool foundation knowledge

- [x] Unity x64 + IL2CPP architecture / metadata v39.
- [x] LuaSystemManager / SharedData / Game / GUI / Network bridges.
- [x] semantic nearby-player/enemy/target state.
- [x] map readiness / movement / GoTo / NPC navigation semantics.
- [x] built-in Auto Train semantic start/stop and combat engine donor.
- [x] skill cooldown / QuickSkill semantics.
- [x] local buff BuffID/DurationTick/Stack.
- [x] bag/item structured runtime state.
- [x] exact NPC shop sell request and server-driven bag update lifecycle.
- [x] revive / Đầu thai exact packet/value semantics + server Revival lifecycle/countdown.
- [x] dynamic GameDialog selection mechanism.
- [x] team/follow runtime schema + exact leave-team request.
- [x] storage move semantics.
- [x] loot / ItemPack semantic engine.
- [x] NPC/map/AutoPath databases.
- [x] MainThread queue/Update/Action.Invoke internals.
- [x] AI routing / context packs / atomic facts / anti-overread layer.
- [x] compact automation API catalog: `database/AUTO_TOOL_API_CATALOG.md`.
- [x] feature state/action/proof contract: `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md`.
- [x] solved-vs-gap matrix: `AUTO_FEATURE_READINESS.md`.

---

# P0 — knowledge directly needed by the auto tool

## P0.1 Runtime scanner contracts

Goal: future AI should be able to implement read-only snapshots without re-reversing object layouts.

Prioritize only fields used by automation:

- [ ] local player: finish exact reusable snapshot contract for RoleID, name, HP/MaxHP, map, position, dead, combat/busy/progress, selected target where not already explicit in canonical docs.
- [ ] nearby PeacePlayers: add position/death only if required for the chosen non-team Buff implementation; identity/HP/MaxHP/faction/name/guild are already VERIFIED.
- [ ] nearby enemies/monsters: add exact live HP/MaxHP fields only if built-in Train/target state does not already expose enough for the intended policy; Type/IsDeath/RoleID/ResID/Position are already documented.
- [x] current map readiness + movement destination semantics.
- [x] bag free space + live item identity (`ID`, `ItemID`, `Site`, `Position` and common fields).
- [x] local buffs/cooldowns relevant to casting decisions.
- [x] team member HP/map/position for follow/support.
- [x] active GameDialog / NPCShop semantic state/lifecycle.

Do not map extra actor fields unless a concrete feature uses them.

## P0.2 Auto Train knowledge

- [x] `C_AutoModel.Train=1` and semantic StartAutoFight path.
- [ ] capture any exact runtime flag/state needed by the external tool to distinguish Train running/stopped if the existing service state is insufficient during implementation.
- [x] target selection/range/chase/skill semantic fields and action donor documented.
- [x] train-center/radius settings documented: `IsTrainInRanger`, `RangerScan` default 500, `GiveUpMonsterOutRanger`, whitelist/lure/skill settings.
- [x] stop/yield -> delegated feature -> map/position proof -> resume contract documented for Sell/Revive/Travel.
- [x] adaptive spot-switch input model documented: rolling deaths, loot events/value, bag pressure, idle/target availability, travel/return proof.

## P0.3 Auto Buff / Nga My

- [x] nearby PeacePlayer schema.
- [x] key Nga My skill IDs and corrected identity.
- [x] cooldown and local buff semantics.
- [ ] verify non-team beneficial-skill acceptance per important skill/relationship actually used by the tool.
- [x] target range/eligibility/chase/cast state guards used by the built-in support donor documented.
- [x] success-proof contract documented: HP/buff/cooldown/progress + fresh rescan.
- [x] production priority policy fields documented: HP%, MaxHP priority, RoleID/name/guild/faction/level filters, existing buff, range, target freshness/death.

## P0.4 Auto Sell / inventory policy

- [x] free bag-space semantic source.
- [x] item instance/template/site/slot distinction.
- [x] sell packet + exact payload.
- [x] server-driven one-mutation -> wait -> rescan rule.
- [ ] build compact static lookup for only fields relevant to keep/sell/use policy:
  - item name/type;
  - sellable/throwable;
  - equipment slot/type;
  - level/star/quality/value fields when useful;
  - protected/quest/special categories.
- [ ] promote/verify vendor candidates needed by the actual configured Train maps; do not map every merchant in the game unnecessarily.
- [x] NPCShop-ready guard and sell completion proof documented.
- [x] return-to-saved-Train map/position proof + resume contract documented.

Do **not** normalize every cosmetic/equipment field merely because `Equips` has 22,763 rows.

## P0.5 NPC Trị liệu

- [x] NPC 339 Đỗ Thanh Đằng / Lâu Lan static identity.
- [x] dynamic GameDialog mechanism.
- [ ] capture actual healer dialog selections at runtime.
- [ ] identify Trị liệu text + current selectionID.
- [ ] record any confirmation step.
- [ ] prove result by HP/money/dialog state.
- [ ] repeat on additional maps only if Auto Heal needs multi-map service routing.

## P0.6 Revive / death recovery

- [x] exact revive packet/type values.
- [x] server Revival state fields `TimeLeft`, newbie/skill availability and open/update/close lifecycle documented.
- [x] death -> choose revive policy -> one action -> Revival close -> alive/spawn/map-ready proof documented.
- [x] safe resume rule documented: do not resume Train until alive + map-ready + valid position.
- [x] saved Train map/position + semantic GoTo return path documented.

## P0.7 Party / follow / multi-client orchestration

- [x] structured team member fields and Follow donor.
- [x] exact leave-team action: `LeaveTeam=4`, payload `4:selfRoleID` through `CMD_TEAM_ACTION`.
- [ ] verify the exact automatic **join-party request** payload/path only if the production feature actually needs automatic joining and no already-proven path is sufficient.
- [x] per-PID independent snapshot/state/action ownership design documented.
- [x] priority arbitration between Revive, map transition, survival, Heal/Buff, Sell, Party, Train, Loot and spot optimization documented.
- [x] adaptive train-spot rotation policy inputs/outputs documented.

## P0.8 MainThread / action boundary

Static dispatcher knowledge is DONE and retained.

Remaining live proof is implementation work:

- [ ] construct/root one valid external managed `System.Action`, enqueue through `MainThread.Execute`, and observe the harmless callback state transition.

Record new client-side facts here only if they are reusable across multiple auto features.

Do not spend general research time re-proving the dispatcher internals.

---

# P1 — static database expansion only where auto needs it

## Skills / combat-support subset

Prioritize fields required for Auto Train/Buff:

- SkillID / Name
- FactionID
- target type
- cast range
- cooldown/group
- weapon/state requirements
- relevant SkillProperties / MagicAttributes
- AutoSkills relations when they explain built-in auto behavior.

No need to fully model progression/book economy unless an auto feature uses it.

## Items / equipment subset

Prioritize Auto Sell / loot / use decisions:

- ItemID / Name / Type
- sellable / throwable
- stack/value
- equipment point/type
- level/star/quality/bound-relevant rules
- medicine usage fields if Auto HP/MP item use is implemented.

## Monsters / maps / NPC subset

Prioritize:

- train target identity;
- boss/monster filtering;
- map/NPC service routing;
- return paths / portal topology if `Game.GoTo` needs support.

Do not normalize 17,121 monster rows into mandatory AI context; use compact index + chunks/lookup.

---

# P2 — conditional auto features only

Only investigate when explicitly building that feature:

- Auto Quest / Tasks / GrowPoints.
- Pet/Spirit auto.
- Storage/Bank automation.
- medicine auto-use beyond current needs.
- offline route planner if stock `Game.GoTo` becomes insufficient.
- combat telemetry only when it improves decisions such as death rate, kill rate or spot switching.

---

# Normally ignore

Unless a concrete auto feature directly depends on them:

- cosmetics/fashion/wings/appearance/model tables;
- visual FX/audio tables;
- LiveKit/voice;
- launcher/update/record-playback internals;
- D3D/rendering/baselib;
- crash handler internals;
- decorative UI resources;
- guild/reputation/title systems;
- exhaustive Translations or `data.unity3d` extraction with no automation use.

---

# Knowledge format for every new auto discovery

Prefer this compact contract:

```text
Feature/subsystem
State source
Exact fields / IDs
Guard conditions
Semantic action
Expected result / server event
Failure / timeout / retry rule
Evidence status
Canonical source
```

Every discovery should make a future build task **smaller**, not make the repository more encyclopedic.

# Core rule

If a piece of research does not help the tool **observe, decide, move, target, cast, interact, sell/store/loot, revive/heal/buff, coordinate clients, or verify success**, defer it.
