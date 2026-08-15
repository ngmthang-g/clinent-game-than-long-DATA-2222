# AI Router — route task before reading deeply

Read `AI_BOOTSTRAP.md` first.

This file answers: **What should I read for the current task?**

Do not select multiple context packs unless the task genuinely spans multiple subsystems. For cross-feature work, use `contexts/BUILD_ORCHESTRATOR.md` instead of loading every feature pack independently.

| Task / question | Primary context pack |
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

## Secondary routes

For quest/task automation, read:

- `AI_BOOTSTRAP.md`
- `analysis/23_TASK_QUEST_AUTOMATION.md`
- `analysis/12_GLOBAL_LUA_HELPERS.md`
- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`.

For Pet/Spirit automation, read:

- `AI_BOOTSTRAP.md`
- `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`
- `contexts/BUILD_MAINTHREAD_BRIDGE.md` if implementation sends mutable actions externally.

For Storage/Bank, read:

- `AI_BOOTSTRAP.md`
- `analysis/26_STORAGE_BANK_ITEM_MOVE.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `contexts/BUILD_MAINTHREAD_BRIDGE.md` for execution.

For ground loot/pickup, read:

- `AI_BOOTSTRAP.md`
- `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

For static data questions about Items/Skills/Monsters/Equips/Magic, read:

- `database/static/README.md`
- `database/static/LOOKUP_GUIDE.md`
- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`
- only the specific index/chunk containing required records **if that chunk has actually been uploaded**.

Do not invent a missing static CSV. The repo currently records schema/counts and tracks full chunk upload separately in `research/TODO.md`.

For exact packets/API names, prefer lookup before broad analysis:

- `database/FACTS.jsonl`
- `database/PACKET_IDS.csv`
- `database/PACKET_CATALOG.md`
- `database/API_QUICK_REFERENCE.md`
- `database/FINDING_TO_DOC_MAP.md`.

## Routing examples

### “Build Auto Buff for selected nearby people”

Read:

1. `AI_BOOTSTRAP.md`
2. `contexts/BUILD_AUTO_BUFF.md`
3. only REQUIRED files listed there.

Do not read Quest/Pet/Storage/Launcher docs.

### “Fix disconnect/crash when actions are invoked”

Read:

1. `AI_BOOTSTRAP.md`
2. `contexts/BUILD_MAINTHREAD_BRIDGE.md`
3. `contexts/BUILD_TOOL_CORE.md` only if action queue/state ownership is also broken.

Do not restart GameAssembly-wide reverse.

### “Find NPC ID and make character walk to it”

Use database lookup first, then `analysis/12_GLOBAL_LUA_HELPERS.md` and `analysis/22_MAP_MINIMAP_RUNTIME.md`. Do not manually invent X/Y.

### “What is ItemID X?”

Use the static-data guide/index strategy. Do not load all 5,238 Items into context, and do not claim an unuploaded chunk is present.

## Hard rule

**A large repository is not an instruction to read everything. It is a library. Route, lookup, then read narrowly.**