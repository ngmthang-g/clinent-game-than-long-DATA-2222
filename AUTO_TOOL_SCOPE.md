# Auto Tool Scope — primary purpose of this knowledge base

This repository exists primarily to support building a large **Thần Long automation tool**. Research that does not materially improve automation reliability, state observation, decision logic, or semantic action execution is secondary and should not consume normal AI context or research time.

## P0 — always relevant to the auto tool

1. Runtime scanner/state
   - local role state;
   - nearby players/enemies/NPCs/monsters/item packs;
   - HP/MaxHP, position, death, target, map readiness;
   - bag/items, buffs, cooldowns, progress/channel state;
   - team/follow state.

2. Semantic action execution
   - Lua/Game/GUI APIs;
   - MainThread dispatcher and safe action boundary;
   - internal target/movement/skill/NPC/UI actions;
   - state proof after every mutable action.

3. Auto Train
   - semantic Train start/stop;
   - target selection/chase/use-skill;
   - train center/radius/return logic;
   - death recovery;
   - loot and bag-space integration;
   - adaptive spot switching.

4. Auto Buff / heal
   - nearby peaceful-player schema;
   - Nga My support skills;
   - HP/MaxHP priority;
   - buff/cooldown/range/target checks;
   - non-team target acceptance where supported.

5. Auto Sell / inventory
   - free bag space;
   - item instance vs template identity;
   - sellable/keep/weapon/equipment filters;
   - NPC shop state;
   - one mutation -> wait server state -> rescan;
   - return-to-train flow.

6. NPC treatment / revive
   - healer NPC discovery;
   - `Game.GetNPCPosition` / `GoToNPC` / `ClickNPC`;
   - dynamic `GameDialog.Selections`;
   - revive/Đầu thai exact actions;
   - HP/money/dialog outcome proof.

7. Party / follow / multi-client orchestration
   - team members and HP/position;
   - join/leave/follow when required;
   - per-PID independent state;
   - max-one-mutable-action gate;
   - feature arbitration.

8. Safety / robustness
   - map loading and UI lifecycle;
   - stale-pointer avoidance;
   - timeout vs state proof;
   - disconnect/crash prevention;
   - Captcha -> pause for user handling.

## P1 — analyze only when it directly improves an auto feature

- Skills / SkillProperties / AutoSkills / MagicAttributes relevant to combat or buff decisions.
- Items / Equips / Medicines / Gems relevant to loot/sell/use/keep policy.
- Maps / NPC / AutoPath / portal data relevant to movement, service routing, train return or spot switching.
- Monsters relevant to target selection, train filtering or boss detection.
- Tasks only if an Auto Quest feature is actually being built.
- Pet/Spirit only if pet/spirit automation is actually being built.
- Translations only when semantic text matching for dialog/UI needs it.
- PathFinder/NodeGrid only when stock `Game.GoTo` / pathing becomes a real blocker.

## P2 / normally ignore

Do not spend research budget on these unless a concrete auto feature depends on them:

- cosmetics, fashion, wings, avatar/model/FX tables;
- audio/voice/LiveKit internals;
- launcher/update internals;
- rendering/D3D12/baselib;
- crash handler internals;
- decorative UI resources;
- guild/reputation/title systems unrelated to an automation feature;
- broad combat analytics that do not improve automation decisions;
- exhaustive asset inventories with no automation use.

## Auto-value test

Before researching a new subsystem, ask:

> Will this information help the tool **observe state, decide, move, target, cast, interact, sell/store/loot, revive/heal, coordinate clients, or verify success more reliably?**

If the answer is no, defer it.

## Preferred knowledge shape

For auto-tool research, preserve compact implementation-oriented facts:

```text
State source
 -> fields / IDs
 -> guard conditions
 -> semantic action
 -> expected server/runtime result
 -> timeout/failure conditions
 -> canonical source
```

Prefer feature contracts and lookup indexes over encyclopedic prose.

## Mandatory AI behavior

For normal work:

```text
AI_BOOTSTRAP.md
 -> AUTO_TOOL_SCOPE.md
 -> AI_ROUTER.md
 -> one matching contexts/BUILD_*.md
 -> only required docs / exact database records
```

Do not expand unrelated client knowledge merely because the data exists.