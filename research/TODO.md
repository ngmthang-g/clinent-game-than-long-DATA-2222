# Research TODO — automation-tool-focused knowledge base

> Main goal: turn this frozen client into a reusable **AI-readable knowledge base for building the Thần Long auto tool**. Do not expand unrelated client knowledge unless it materially improves an automation feature.

Read `AUTO_TOOL_SCOPE.md` before adding new research.

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
- [x] revive / Đầu thai exact packet/value semantics.
- [x] dynamic GameDialog selection mechanism.
- [x] team/follow runtime schema.
- [x] storage move semantics.
- [x] loot / ItemPack semantic engine.
- [x] NPC/map/AutoPath databases.
- [x] MainThread queue/Update/Action.Invoke internals.
- [x] AI routing / context packs / atomic facts / anti-overread layer.

---

# P0 — knowledge directly needed by the auto tool

## P0.1 Runtime scanner contracts

Goal: future AI should be able to implement read-only snapshots without re-reversing object layouts.

Prioritize only fields used by automation:

- [ ] local player: RoleID, name, HP/MaxHP, map, position, dead, combat/busy/progress, selected target.
- [ ] nearby PeacePlayers: identity, HP/MaxHP, faction, position/death if needed for Buff.
- [ ] nearby enemies/monsters: identity/template, HP/MaxHP, position, alive/dead, reachability/target relevance.
- [ ] current map readiness + movement destination.
- [ ] bag free space + live items (`ID`, `ItemID`, `Site`, `Position`, quantity/bound/durability as needed).
- [ ] local buffs/cooldowns relevant to casting decisions.
- [ ] team member HP/map/position for follow/support.
- [ ] active GameDialog / NPCShop state where needed.

Do not map extra actor fields unless a concrete feature uses them.

## P0.2 Auto Train knowledge

- [x] `C_AutoModel.Train=1` and semantic StartAutoFight path.
- [ ] capture exact runtime guards/state that define Train running/stopped/loading/dead.
- [ ] document target selection/range/chase/skill fallback fields required by production state machine.
- [ ] document train-center/radius/return constraints actually exposed by Lua/settings.
- [ ] document reliable stop/resume semantics across map change/death/sell/heal.
- [ ] document adaptive spot-switch signals: deaths/time window, bag/loot rate, target availability, return success.

## P0.3 Auto Buff / Nga My

- [x] nearby PeacePlayer schema.
- [x] key Nga My skill IDs and corrected identity.
- [x] cooldown and local buff semantics.
- [ ] verify non-team beneficial-skill acceptance per important skill.
- [ ] map exact target range/eligibility/state guards used by built-in heal/buff donor.
- [ ] document success proof: HP change / buff appearance / cooldown / progress.
- [ ] define production priority policy fields: HP%, MaxHP priority, whitelist, distance, existing buff, death state.

## P0.4 Auto Sell / inventory policy

- [x] free bag-space semantic source.
- [x] item instance/template/site/slot distinction.
- [x] sell packet + payload.
- [x] server-driven rescan rule.
- [ ] build compact static lookup for only fields relevant to keep/sell/use policy:
  - item name/type;
  - sellable/throwable;
  - equipment slot/type;
  - level/star/quality/value fields when useful;
  - protected/quest/special categories.
- [ ] map/verify vendor candidates needed by actual train maps.
- [ ] document NPCShop-ready guard and sell completion proof.
- [ ] document return-to-train state after selling.

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
- [ ] document death-detection -> countdown/availability -> action -> map/spawn-ready proof.
- [ ] document safe resume rules for Auto Train after revive.
- [ ] integrate saved train map/position and path-back semantics.

## P0.7 Party / follow / multi-client orchestration

- [x] structured team member fields and Follow donor.
- [ ] map exact join/leave/invite/accept actions only if production feature needs them.
- [ ] define per-PID independent snapshot/action ownership.
- [ ] define priority arbitration between Revive, Heal, Sell, Return, Buff, Train.
- [ ] document adaptive train-spot rotation policy inputs/outputs.

## P0.8 MainThread / action boundary

Static dispatcher knowledge is DONE and retained.

Remaining live proof is implementation work, but any new client-side facts discovered during implementation should be recorded here only if they are reusable across features.

Do not spend general research time re-proving the dispatcher.

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