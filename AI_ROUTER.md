# AI Router — route automation task before reading deeply

Read `AI_BOOTSTRAP.md` and `AUTO_TOOL_SCOPE.md` first.

This file answers: **What should I read for the current automation/tool task?**

Do not select multiple context packs unless the task genuinely spans multiple subsystems. For cross-feature work, use `contexts/BUILD_ORCHESTRATOR.md` instead of loading every feature pack independently.

## Compact auto-tool references

Before opening broad analysis, use these when useful:

- `database/AUTO_TOOL_API_CATALOG.md` — auto-only state/query/action API catalog with exact high-value IDs/payloads and narrow remaining gaps.
- `analysis/34_AUTO_STATE_ACTION_PROOF_MATRIX.md` — per-feature `state -> guard -> one action -> proof -> failure/rescan` contract.

They are compact implementation summaries; canonical subsystem documents remain the evidence source when exact provenance or edge cases matter.

| Auto-tool task / question | Primary context pack |
|---|---|
| Build/refactor tool architecture, multi-client, state machine, action arbitration | `contexts/BUILD_TOOL_CORE.md` |
| Read nearby players/entities, local player, target, map objects, bag state | `contexts/BUILD_RUNTIME_SCANNER.md` |
| Execute semantic actions safely on Unity thread, Action/delegate bridge | `contexts/BUILD_MAINTHREAD_BRIDGE.md` |
| Auto Train / đánh quái / target/chase/skill/loot | `contexts/BUILD_AUTO_TRAIN.md` |
| Auto Buff / Nga My / nearby-player heal / HP priority | `contexts/BUILD_AUTO_BUFF.md` |
| Auto Sell / bag full / vendor / item filtering | `contexts/BUILD_AUTO_SELL.md` |
| NPC Trị liệu / healer / GameDialog semantic selection | `contexts/BUILD_AUTO_HEAL.md` |
| Đầu thai / revive / death recovery | `contexts/BUILD_AUTO_REVIVE.md` |
| Party/team/join/leave/follow/member data | `contexts/BUILD_PARTY.md` |
| Adaptive Train + Party + Buff + Sell + Revive + spot switching | `contexts/BUILD_ORCHESTRATOR.md` |

## Direct supporting routes for automation

### Ground loot / pickup

Read only:

- `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

### Skill / buff lookup

Use lookup first:

- `database/AUTO_TOOL_API_CATALOG.md`
- `database/NGAMY_SUPPORT_SKILLS.md`
- `database/FACTS.jsonl`
- `database/static/README.md` / `LOOKUP_GUIDE.md` when an exact static record is actually needed for an auto decision.

Do not load every skill/config table merely to implement one cast rule.

### Item/equipment lookup for Auto Sell / loot

Use only the records needed for the current keep/sell/use policy. Runtime `GetItemType`, `GetEquipType`, `IsItemSellable` and current live instance fields remain action-time truth.

### NPC/service/navigation

Use:

- NPC database / service candidate index;
- `analysis/12_GLOBAL_LUA_HELPERS.md`;
- `analysis/22_MAP_MINIMAP_RUNTIME.md`;
- actual `GameDialog` / NPCShop runtime state.

Do not invent static X/Y when `Game.GetNPCPosition(npcID)` exists.

### Exact packet/API lookup

Prefer:

- `database/AUTO_TOOL_API_CATALOG.md`
- `database/FACTS.jsonl`
- `database/PACKET_IDS.csv`
- `database/PACKET_CATALOG.md`
- `database/API_QUICK_REFERENCE.md`
- `database/FINDING_TO_DOC_MAP.md`.

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
- launcher/update internals;
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

### “Find NPC ID and make character walk to it”

Use database lookup first, then `analysis/12_GLOBAL_LUA_HELPERS.md` and `analysis/22_MAP_MINIMAP_RUNTIME.md`. Do not manually invent X/Y.

### “What should Auto Sell keep?”

Read `contexts/BUILD_AUTO_SELL.md`; query only item/equipment fields needed by the policy. Do not load all Items/Equips tables.

## Hard rule

**This is an automation-tool knowledge library, not an encyclopedia of the whole client. Route, lookup, then read narrowly.**
