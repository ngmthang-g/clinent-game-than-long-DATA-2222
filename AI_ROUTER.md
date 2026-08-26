# AI Router — route automation task before reading deeply

Read `AI_BOOTSTRAP.md` and `AUTO_TOOL_SCOPE.md` first.

This file answers: **What should I read for the current automation/tool task?**

Do not select multiple context packs unless the task genuinely spans multiple subsystems. For cross-feature work, use `contexts/BUILD_ORCHESTRATOR.md` instead of loading every feature pack independently.

## Compact auto-tool references

Before opening broad analysis, use these when useful:

- `AUTO_FEATURE_READINESS.md` — solved vs targeted-proof vs design-only status for each automation feature.
- `research/AUTO_RUNTIME_PROOF_QUEUE.md` — **only the remaining live/runtime proofs worth collecting**; use this instead of inventing new broad reverse work.
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md` — exact per-PID read-only external snapshot model and field boundaries.
- `database/AUTO_TOOL_API_CATALOG.md` — auto-only state/query API catalog.
- `database/AUTO_TOOL_ACTION_CATALOG.md` — **exact semantic mutable actions**, packet IDs/payloads and result-proof rules.
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md` — per-feature `state -> guard -> one action -> proof -> failure/rescan` matrix.
- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` — exact static anchors for PC multi-instance InputSync, `TryClickUI`, UIButton and UI drag-state resolution; use for hidden-click/sync resolver failures.

These are compact implementation summaries; canonical subsystem documents remain the evidence source when exact provenance or edge cases matter.

| Auto-tool task / question | Primary context pack |
|---|---|
| Build/refactor tool architecture, multi-client, state machine, action arbitration | `contexts/BUILD_TOOL_CORE.md` |
| Read nearby players/entities, local player, target, map objects, bag state | `contexts/BUILD_RUNTIME_SCANNER.md` |
| Execute semantic actions safely on Unity thread, Action/delegate bridge | `contexts/BUILD_MAINTHREAD_BRIDGE.md` |
| Hidden internal click / `TryClickUI` / InputSync / press-release-drag-state / multi-instance sync resolver | `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md` |
| Auto Train / đánh quái / target/chase/skill/loot | `contexts/BUILD_AUTO_TRAIN.md` |
| Auto Buff / Nga My / nearby-player heal / HP priority | `contexts/BUILD_AUTO_BUFF.md` |
| Auto Sell / bag full / vendor / item filtering | `contexts/BUILD_AUTO_SELL.md` |
| NPC Trị liệu / healer / GameDialog semantic selection | `contexts/BUILD_AUTO_HEAL.md` |
| Đầu thai / revive / death recovery | `contexts/BUILD_AUTO_REVIVE.md` |
| Party/team/join/leave/follow/member data | `contexts/BUILD_PARTY.md` |
| Adaptive Train + Party + Buff + Sell + Revive + spot switching | `contexts/BUILD_ORCHESTRATOR.md` |

## Direct supporting routes for automation

### Exact action / packet question

Start with:

- `database/AUTO_TOOL_ACTION_CATALOG.md`

It already consolidates the important solved mutations for Train, movement, skill use, NPC/GameDialog, Sell, item actions, loot, Revive, Team join/leave/invite and Follow.

Only open `database/PACKET_IDS.csv` / subsystem analysis when the action catalog does not contain the required operation.

### Ground loot / pickup

Read only:

- `database/AUTO_TOOL_ACTION_CATALOG.md`
- `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md` if detailed filter/lifecycle evidence is needed.

### Skill / buff lookup

Use lookup first:

- `database/AUTO_TOOL_API_CATALOG.md`
- `database/AUTO_TOOL_ACTION_CATALOG.md`
- `database/NGAMY_SUPPORT_SKILLS.md`
- `database/FACTS.jsonl`
- exact static record only if a concrete auto decision needs it.

Do not load every skill/config table merely to implement one cast rule.

### Item/equipment lookup for Auto Sell / loot

Use:

- `contexts/BUILD_AUTO_SELL.md`
- `database/AUTO_SELL_CLASSIFICATION.md`
- live runtime `GetItemType`, `GetEquipType`, `IsItemSellable`
- targeted static rows only when a richer keep/sell policy requires them.

Do not load all 5,238 Items or 22,763 Equips.

### NPC/service/navigation

For Auto Sell vendor selection, start with:

- `database/AUTO_SELL_VENDOR_MAP.md`.

For broader discovery only when needed, use:

- `database/NPC_SERVICE_CANDIDATES.md` / NPC chunks;
- `analysis/12_GLOBAL_LUA_HELPERS.md`;
- `analysis/22_MAP_MINIMAP_RUNTIME.md`;
- actual `GameDialog` / `NPCShop` runtime state.

Do not invent static X/Y when `Game.GetNPCPosition(npcID)` exists.

### Party/join/follow

Use `contexts/BUILD_PARTY.md` first.

Already solved and must not be retraced:

```text
leave team -> CMD_TEAM_ACTION 200057 -> 4:selfRoleID
join target's team -> CMD_OTHER_ROLE_COMMAND 200051 -> 9:targetRoleID
invite target -> CMD_OTHER_ROLE_COMMAND 200051 -> 5:targetRoleID
```

Membership success still requires fresh TeamID/C_TeamData proof.

### Hidden click / InputSync / multi-instance sync

Start with:

- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md` only when launcher/session control is part of the problem.

Verified static anchors include `SyncBootstrap.AutoInit`, `InputSyncManager`, `TryClickUI`, `FramePressState`, UI drag-state helpers, `UIButton.HandleClickEvent`, instance/master/group/UDP evidence and official record/playback components.

Do **not** invent method signatures from string names. For a machine-specific failure, verify snapshot hashes and separate resolver/init/PID/window/Screen/UI-drag-state causes before blaming a different game build or CPU model.

### Feature is statically solved but one live behavior is missing

Read:

1. `AUTO_FEATURE_READINESS.md`
2. `research/AUTO_RUNTIME_PROOF_QUEUE.md`
3. exactly the one feature/context document named by that proof.

Do **not** broad-reverse the client again merely because runtime validation has not yet been performed.

Current highest-value queued proofs are:

```text
P0 external managed Action -> MainThread live callback
P1 non-team Nga My beneficial-skill acceptance
P1 exact Trị liệu dialog/result
P1 Lâu Lan vendor -> normal NPCShop promotion
```

## Conditional routes — only when that auto feature is actually requested

Quest/task automation:

- `analysis/23_TASK_QUEST_AUTOMATION.md`
- `analysis/12_GLOBAL_LUA_HELPERS.md`
- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`.

Pet/Spirit automation:

- `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`.

Storage/Bank automation:

- `analysis/26_STORAGE_BANK_ITEM_MOVE.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

Do not research these domains merely because they exist in Config.

## Normally out of route

Unless a concrete auto feature depends on them, do not spend context/research on:

- cosmetics/fashion/appearance/FX;
- voice/LiveKit;
- launcher/update internals except when diagnosing the documented PC InputSync/launcher-control path;
- D3D/rendering/baselib;
- decorative UI assets;
- guild/title/reputation systems;
- broad analytics unrelated to auto decisions.

## Routing examples

### “Build Auto Buff for selected nearby people”

Read:

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `contexts/BUILD_AUTO_BUFF.md`
4. only REQUIRED files listed there.

Do not read Quest/Pet/Storage/Launcher docs.

### “Fix disconnect/crash when actions are invoked”

Read:

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `contexts/BUILD_MAINTHREAD_BRIDGE.md`
4. `contexts/BUILD_TOOL_CORE.md` only if action queue/state ownership is also broken.

Do not restart GameAssembly-wide reverse.

### “Fix hidden click / InputSync resolver failure on another PC”

Read:

1. `CLIENT_MANIFEST.md` for exact snapshot hashes;
2. `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`;
3. `analysis/07_SUPPORT_MODULES_LAUNCHER.md` only if launcher master/group/session state is relevant.

Do not assume Xeon/CPU or a different client binary before checking the hash, resolver, startup timing, PID, window/Screen and drag-state evidence.

### “Find NPC ID and make character walk to it”

Use database lookup first, then `database/AUTO_TOOL_ACTION_CATALOG.md` and `analysis/12_GLOBAL_LUA_HELPERS.md`. Do not manually invent X/Y.

### “What should Auto Sell keep?”

Read `contexts/BUILD_AUTO_SELL.md` and `database/AUTO_SELL_CLASSIFICATION.md`; query only item/equipment fields needed by the policy.

## Hard rule

**This is an automation-tool knowledge library, not an encyclopedia of the whole client. Route, lookup, then read narrowly.**