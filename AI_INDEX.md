# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## IMPORTANT: compact entrypoint changed

This repository is now intentionally optimized for a **large AI-native knowledge base**. Future AI should **not read this entire index plus every analysis file before starting a task**.

Normal task flow:

1. `AI_BOOTSTRAP.md` — compact architecture/fact guardrails.
2. `AI_ROUTER.md` — map current task to one context pack.
3. exactly one matching `contexts/BUILD_*.md` pack.
4. only the REQUIRED documents named by that pack.
5. database lookup for specific IDs/records as needed.

Use this `AI_INDEX.md` as the **deep repository map** when broader navigation is needed.

## Purpose

This repository is the canonical technical memory for this frozen Thần Long client snapshot. Future AI must read the knowledge base before doing new reverse engineering, but should do so through the routing layer above to avoid context overload.

The KB is **not a verbatim chat dump**. Exact technical facts are preserved exactly; repeated discussion, dead ends and exploratory wording are deduplicated into structured documents. Read `KB_METHOD.md` for the preservation/evidence policy.

## Routing layer

- `AI_BOOTSTRAP.md` — short mandatory bootstrap.
- `AI_ROUTER.md` — task -> context-pack router.
- `contexts/README.md` — context-pack usage rules.
- `contexts/BUILD_TOOL_CORE.md`
- `contexts/BUILD_RUNTIME_SCANNER.md`
- `contexts/BUILD_MAINTHREAD_BRIDGE.md`
- `contexts/BUILD_AUTO_TRAIN.md`
- `contexts/BUILD_AUTO_BUFF.md`
- `contexts/BUILD_AUTO_SELL.md`
- `contexts/BUILD_AUTO_HEAL.md`
- `contexts/BUILD_AUTO_REVIVE.md`
- `contexts/BUILD_PARTY.md`
- `contexts/BUILD_ORCHESTRATOR.md`.

Read-budget target for a normal implementation task: **5–10 documents before coding**, not the entire repo.

## Evidence labels

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — strong evidence, not yet end-to-end runtime verified.
- **HYPOTHESIS** — proposed direction requiring validation.
- **SOURCE-INSPECTED DONOR** — behavior/UX/state policy observed in older tool source; useful donor, but not automatically runtime-verified in the new architecture.

Never silently promote a prediction into VERIFIED.

## Frozen snapshot / Git LFS rule

The owner intentionally keeps this repo as one fixed client snapshot. Do not request a new hash/version check every session.

GitHub Contents may show `.dll/.exe/.dat` as ~130-byte LFS pointers. Deep reverse used the real original bytes. If new native disassembly is genuinely required, use original LFS/local bytes, not pointer text.

# Major breakthroughs already solved

## Phase 1 — IL2CPP architecture

Client is Unity Windows x64 + IL2CPP. `global-metadata.dat` is metadata version 39. `GameAssembly.dll` exposes a broad `il2cpp_*` runtime API surface.

Core bridge classes include:

- `FGStudio.LuaSystem.LuaSystemManager`
- `FGStudio.LuaSystem.LuaSystemSharedData`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Game`
- `FGStudio.LuaSystem.API.LuaSystemAPI_GUI`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Network`
- `FGStudio.LuaSystem.GUI.UIButton`.

## Phase 2 — decrypted semantic data

Custom bundle decrypt was reproduced sufficiently to extract Config/Interface/Lua data.

Recovered:

- **75 Config XML TextAssets**
- **338 UI layout XML TextAssets**
- **1,469 UI handler bindings**
- **339 high-level Lua script classes** + global infrastructure
- **169 TCP packet constants**.

For UI/gameplay investigation, use this priority:

`Lua source -> Config/Layout semantic data -> exact handler/payload -> native reverse only if still needed`.

## Phase 3 — structured runtime/UI data

Shipped UI proves semantic runtime APIs for nearby players, selected targets, bag/items, buffs, skill cooldowns, map readiness, team members, pet/spirit and tasks.

Examples:

- `Game.GetNearByPeacePlayers(limit)` exposes RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank.
- `Game.SelectedTarget` exposes target identity/vitals/type state.
- `Game.GetSkillCooldown(skillID)` exposes passed/cooldown ticks.
- `Game.GetBuffs()` exposes BuffID/DurationTick/Stack.
- `Game.GetItemsAtSite(Site)` is the semantic bag/storage source.
- `Game.IsMapReady`, `GetLocalMapObjects`, `GetNearbyObjects`, `MoveTo`, `GoTo` provide map/movement state.

## Phase 4 — MainThread dispatcher is statically solved

`FGStudio.Engine.Utilities.MainThread` is no longer just a candidate.

Direct GameAssembly disassembly verifies:

- `.ctor()` creates `ConcurrentQueue<System.Action>` at `this+0x20`;
- `Awake()` sets singleton Instance;
- `Execute(Action)` enqueues into the queue;
- `Update()` calls `DoExecuteWorks()`;
- `DoExecuteWorks()` loops queue state -> dequeue -> `Action.Invoke` until empty.

Exact frozen-snapshot RVAs are documented in `analysis/21_MAIN_THREAD_DISPATCHER.md`.

Game-owned network producers (`TCPGame` and `TCPLogin` SocketCommand/Event handlers) themselves construct legitimate managed `System.Action` objects and call `MainThread.Execute`. See `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`.

Therefore the internal dispatcher chain is VERIFIED. Remaining work is only the external bridge proof: safely construct/root a managed Action, enqueue one harmless callback, and prove it executes on Unity Update thread.

# Canonical analysis documents

## Architecture / reverse foundation

- `analysis/00_MASTER_RESEARCH_MAP.md` — file priority and architecture map
- `analysis/01_IL2CPP_RUNTIME_METADATA.md` — IL2CPP/metadata/runtime surface
- `analysis/02_LUA_GAME_UI_NETWORK_API.md` — Lua/Game/GUI/Network bridge
- `analysis/03_WORLD_ENTITY_MAP_PATH.md` — world/entity/map/path
- `analysis/04_INVENTORY_ITEMS_SHOP.md` — inventory/item/shop foundation
- `analysis/05_COMBAT_SKILLS_BUFFS.md` — combat/skills/buffs
- `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` — FG decrypt and Unity bundles
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md` — launcher/support modules
- `analysis/08_FILE_BY_FILE_CATALOG.md` — file-by-file reverse value
- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md` — decrypted Config/Interface/Lua results.

## Gameplay/UI semantic subsystems

- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` — Train/PK/Quest/FuBen auto engine
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md` — exact packet/action payloads
- `analysis/12_GLOBAL_LUA_HELPERS.md` — `GoToNPC`, `GoToMonster`, reusable helpers
- `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` — UI event/action architecture
- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` — nearby peaceful/enemy player + target schema
- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` — Nga My donor and corrected skill identity
- `analysis/16_PLAYER_INTERACTION_UI_API.md` — player/social target actions/data
- `analysis/17_BUFF_RUNTIME_SCHEMA.md` — buff ID/duration/stack/properties/events
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md` — skill cooldown and F-key semantics
- `analysis/19_PROGRESS_CAPTCHA_SAFETY.md` — progress/channel/Captcha guard
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md` — bag events/NPCShop/Quick Sell
- `analysis/21_MAIN_THREAD_DISPATCHER.md` — exact MainThread queue/Update/Action.Invoke chain
- `analysis/22_MAP_MINIMAP_RUNTIME.md` — map-ready/local objects/movement
- `analysis/23_TASK_QUEST_AUTOMATION.md` — structured Task/Auto Quest donor
- `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` — Pet/Spirit runtime and auto behavior
- `analysis/25_TEAM_RUNTIME_FOLLOW.md` — team state/HP/position/actions/Follow
- `analysis/26_STORAGE_BANK_ITEM_MOVE.md` — storage item move + bank money semantics
- `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md` — item-pack/loot scan/filter/pickup
- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` — Items/Skills/Magic/Monsters/Equips normalized schemas
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md` — game-owned Action construction + MainThread.Execute producers.

## Older-tool source donor / orchestration

- `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md` — source audit of Auto Buff v1.3.1; keep UX/state-policy donors, reject legacy remote-worker mutable-action path
- `features/AUTO_ORCHESTRATOR.md` — coordinated Train/Party/Buff/Sell/Revive/spot switching and adaptive orchestration.

# Database navigation

Start at:

- `database/README.md`
- `database/FINDING_TO_DOC_MAP.md`
- `database/FACTS_README.md`
- `database/FACTS.jsonl` — atomic high-value facts for fast lookup.

High-value databases:

- `database/MAPS.csv` — 193 maps
- `database/npcs/NPCS_*.csv` — 1,003 NPCs
- `database/NPC_SERVICE_CANDIDATES.md`
- `database/FUBEN_SCENARIOS.csv`
- `database/AUTOPATH_PORTAL_EDGES.csv`
- `database/AUTOPATH_ITEM_DESTINATIONS.csv`
- `database/autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- `database/PACKET_IDS.csv`
- `database/PACKET_CATALOG.md`
- `database/API_QUICK_REFERENCE.md`
- `database/UI_LAYOUT_CALLBACKS.md`
- `database/LUA_SCRIPT_CATALOG.md`
- `database/UI_PACKET_LIFECYCLE.md`
- `database/AUTO_SETTINGS_SCHEMA.md`
- `database/NGAMY_SUPPORT_SKILLS.md`
- `database/static/README.md` — navigation/schema for the large normalized Config databases.

Large Items/Skills/Magic/Monsters/Equips CSV chunks are lookup data. Do not load all of them into context; locate the relevant record/chunk first.

# Feature specs

- `features/AUTO_TRAIN.md`
- `features/AUTO_BUFF.md`
- `features/AUTO_SELL.md`
- `features/AUTO_REVIVE.md`
- `features/AUTO_HEAL_NPC.md`
- `features/AUTO_ORCHESTRATOR.md`.

# High-value exact facts

## Auto Train

`C_AutoModel.Train = 1`.

Shipped wrapper:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

The visible `Đánh quái` settings tab is not the actual Train start action.

## Nearby peaceful players

Shipped UI reads from `Game.GetNearByPeacePlayers(limit)`:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

Do not restart with CE HP scans for those fields.

## Nga My skill identity correction

Frozen Config truth:

- 406 = Phật Quang Phổ Chiếu
- **407 = Xung Hư Dưỡng Khí**
- 408 = Khởi Tử Hồi Sinh
- **423 = Kim Châm Độ Kiếp**
- 424 = Thanh Tâm Phổ Thiện Chú.

Legacy Lua variable `KIMCHAMDOKIEP` misleadingly points to 407. Do not copy that naming bug.

## Auto Sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

payload:

`itemInstanceID:NpcShopID:ShopID`.

Mutation rule: one current instance -> one sell -> wait server/item event -> rescan.

## Storage move

`CMD_ITEM_ACTION = 100005`, Move action = `5`.

Payload:

`5:itemInstanceID:destinationSite`.

Bag=10; Storage pages=11..15.

## Revive / Đầu thai

`CMD_REVIVE_DATA = 200063`

- normal/Đầu thai = 1
- newbie = 2
- skill revive = 3.

## Dynamic NPC dialog

`Selections[selectionID] = visibleText`.

Submit through `CMD_SHOW_GAMEDIALOG = 100007` with:

`selectionID:SelectedItemID`.

Normally SelectedItemID is `-1` when no item reward selection is involved.

## Lâu Lan healer candidate

Map 5 = Lâu Lan.

- NPC 337 Đỗ Bất Đằng — `LangZhong1`
- NPC 338 Đỗ Hoàng Đằng — `LangZhong1`
- NPC 339 Đỗ Thanh Đằng — `LangZhong1`.

NPC 339 is a strong static healer candidate; exact Trị liệu dialog selection remains server/runtime data and must not be invented.

## Weapon classification

For static `Equips.xml`, `EquipPoint=0` is Weapon. Do not classify weapon templates only as `Type<10`, because weapon subtypes also include Blade/Sickle/Zither outside that range.

# Architecture guardrail

Canonical production direction:

`Resolver -> read-only Scanner -> Snapshot Store -> Observer -> State Machine -> Safety Guard -> Action Queue(max 1 mutable action) -> valid System.Action -> MainThread.Execute -> semantic Game/Lua/UI action -> state proof`

Do not use:

- production `CreateRemoteThread`/continuous remote worker for gameplay mutations;
- arbitrary-thread direct Unity/Lua action invocation;
- stale UIButton pointers;
- screen coordinates when semantic API exists;
- fixed Sleep as success proof;
- response handlers as request actions;
- hardcoded RVA as sole identity;
- OCR/CE scans when structured game data already exists;
- invented NPC coordinates instead of `Game.GetNPCPosition`;
- invented Trị liệu selection IDs;
- automated Captcha solving/bypass.

# Current bottlenecks

Broad reverse is no longer the task. Remaining work is targeted:

1. external managed `System.Action` construction/rooting + harmless live `MainThread.Execute` proof;
2. runtime/server-dynamic NPC Trị liệu selection proof;
3. non-team beneficial-skill acceptance proof for Auto Buff;
4. selected social/party runtime actions where source semantics remain incomplete;
5. continue expanding/uploading large normalized static CSV chunks as needed, but keep them query-oriented rather than mandatory reading.

Read `research/TODO.md` before doing any further reverse work.