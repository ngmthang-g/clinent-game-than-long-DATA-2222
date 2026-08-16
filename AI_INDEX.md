# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## IMPORTANT: compact entrypoint

This repository is intentionally optimized as a **large AI-native knowledge base**. Future AI should **not read this entire index plus every analysis file before starting a task**.

Normal task flow:

1. `AI_BOOTSTRAP.md` — compact architecture/fact guardrails.
2. `AI_ROUTER.md` — route current task.
3. exactly one matching `contexts/BUILD_*.md` pack when implementation work is requested.
4. only REQUIRED documents named by that pack.
5. `database/SUBSYSTEM_SOURCE_MAP.md` when the question is “where is the truth for this subsystem?”.
6. specific database/atomic-fact lookup as needed.

Use this `AI_INDEX.md` as the **deep repository map**, not mandatory full-context reading.

## Purpose

This repository is the canonical technical memory for one frozen Thần Long client snapshot. It exists so future AI does not repeat broad reverse engineering already completed.

The KB is **not a verbatim chat dump**. Exact technical facts are preserved; repeated discussion/dead ends are deduplicated into stable subsystem documents. Read `KB_METHOD.md` for preservation/evidence rules.

## Routing layer

- `AI_BOOTSTRAP.md` — short mandatory bootstrap.
- `AI_ROUTER.md` — task -> context-pack router.
- `contexts/README.md` — context-pack usage rules.
- `database/SUBSYSTEM_SOURCE_MAP.md` — subsystem -> runtime/Lua/Config/protocol source map.
- `database/FINDING_TO_DOC_MAP.md` — finding -> canonical document.
- `database/FACTS.jsonl` — atomic exact facts/IDs/constants.

Implementation context packs:

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

Read-budget target for a normal task: **5–10 documents before coding**, not the entire repo.

## Evidence labels

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — strong evidence, not yet end-to-end/runtime verified.
- **HYPOTHESIS** — proposed direction requiring validation.
- **SOURCE-INSPECTED DONOR** — behavior/policy from older source; useful but not automatically canonical runtime architecture.

Never silently promote a prediction into VERIFIED.

## Frozen snapshot / Git LFS rule

The owner intentionally keeps this repo as one fixed client snapshot. Do not request a new hash/version check every session.

GitHub Contents may show LFS-managed `.dll/.exe/.dat` as tiny pointer text. Deep native analysis used the real original bytes. If new native disassembly is genuinely required, use original LFS/local bytes, not pointer text.

---

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

Custom FG bundle transform was understood sufficiently to decode/extract the important semantic bundles.

Recovered:

- **75 Config XML TextAssets**
- **338 UI layout XML TextAssets**
- **1,469 UI handler bindings**
- **339 high-level Lua script classes** + global infrastructure
- **169 TCP packet constants**.

`Config.unity3d` and `Interface.unity3d` are no longer speculative content sources; their major contents are VERIFIED extracted evidence. See `analysis/08_FILE_BY_FILE_CATALOG.md` and `research/VERIFIED_PHASE2.md`.

For UI/gameplay investigation, prefer:

`Lua source -> Config/Layout semantic data -> exact handler/payload -> native reverse only if still needed`.

## Phase 3 — structured runtime/UI semantics

Shipped UI/Lua proves semantic runtime APIs for nearby players, selected targets, bag/items, buffs, skill cooldowns, map readiness, team, pet/spirit, tasks and loot.

Examples:

- `Game.GetNearByPeacePlayers(limit)` -> RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank.
- `Game.SelectedTarget` -> target identity/vitals/type state.
- `Game.GetSkillCooldown(skillID)` -> passed/cooldown ticks.
- `Game.GetBuffs()` -> BuffID/DurationTick/Stack.
- `Game.GetItemsAtSite(Site)` -> structured bag/storage items.
- `Game.IsMapReady`, `GetLocalMapObjects`, `GetNearbyObjects`, `MoveTo`, `GoTo` -> map/movement state.
- built-in loot uses semantic ItemPack queries/path/click/pickup.

## Phase 4 — MainThread dispatcher native chain solved

`FGStudio.Engine.Utilities.MainThread` is no longer just a candidate.

Direct GameAssembly disassembly verifies:

- `.ctor()` creates `ConcurrentQueue<System.Action>` at `this+0x20`;
- `Awake()` sets singleton Instance;
- `Execute(Action)` enqueues;
- `Update()` calls `DoExecuteWorks()`;
- `DoExecuteWorks()` dequeues and invokes Actions until empty.

Game-owned `TCPGame` / `TCPLogin` producer handlers themselves construct legitimate managed `System.Action` delegates and call `MainThread.Execute`.

Canonical evidence:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md` for delegate-construction ABI/proof design.

## Phase 5 — knowledge/data scaling without AI overread

The repo now has a second layer dedicated to **large-data navigation**:

- `analysis/32_CONFIG_DOMAIN_ATLAS.md` — groups all 75 Config tables by gameplay domain and tool value.
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` — identifies the highest-value Config data still worth normalizing and exact preservation schemas.
- `database/SUBSYSTEM_SOURCE_MAP.md` — tells AI whether a subsystem truth belongs in runtime API, Lua/UI, Config DB or packet/action evidence.
- `database/FACTS.jsonl` — atomic high-value facts including key Config row counts.

This is important because the correct strategy is **index -> exact subsystem -> exact record**, not “read all Config/Lua/analysis”.

---

# Canonical analysis documents

## Architecture / reverse foundation

- `analysis/00_MASTER_RESEARCH_MAP.md` — architecture/file priority.
- `analysis/01_IL2CPP_RUNTIME_METADATA.md` — IL2CPP/metadata/runtime surface.
- `analysis/02_LUA_GAME_UI_NETWORK_API.md` — Lua/Game/GUI/Network bridge.
- `analysis/03_WORLD_ENTITY_MAP_PATH.md` — world/entity/map/path.
- `analysis/04_INVENTORY_ITEMS_SHOP.md` — inventory/item/shop foundation.
- `analysis/05_COMBAT_SKILLS_BUFFS.md` — combat/skills/buffs.
- `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` — FG decrypt and Unity bundles.
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md` — support/launcher modules.
- `analysis/08_FILE_BY_FILE_CATALOG.md` — current file-by-file reverse value; updated after successful Config/Interface extraction.
- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md` — decrypted Config/Interface/Lua results.

## Gameplay/UI semantic subsystems

- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` — Train/PK/Quest/FuBen engine.
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md` — exact packet/action payloads.
- `analysis/12_GLOBAL_LUA_HELPERS.md` — `GoToNPC`, `GoToMonster`, helpers.
- `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` — UI event/action architecture.
- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` — nearby peaceful/enemy + SelectedTarget schema.
- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` — Nga My donor/corrected skill identity.
- `analysis/16_PLAYER_INTERACTION_UI_API.md` — player/social target data/actions.
- `analysis/17_BUFF_RUNTIME_SCHEMA.md` — BuffID/duration/stack/properties/events.
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md` — skill cooldown/QuickSkills/F-key semantics.
- `analysis/19_PROGRESS_CAPTCHA_SAFETY.md` — progress/Captcha guard.
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md` — bag events/NPCShop/Quick Sell.
- `analysis/21_MAIN_THREAD_DISPATCHER.md` — exact queue/Update/Action.Invoke chain.
- `analysis/22_MAP_MINIMAP_RUNTIME.md` — map readiness/local objects/movement.
- `analysis/23_TASK_QUEST_AUTOMATION.md` — Task schema/Auto Quest donor.
- `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` — Pet/Spirit runtime/auto behavior.
- `analysis/25_TEAM_RUNTIME_FOLLOW.md` — team HP/position/actions/Follow.
- `analysis/26_STORAGE_BANK_ITEM_MOVE.md` — storage move/bank semantics.
- `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md` — semantic ItemPack/loot engine.
- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` — normalized Items/Skills/Magic/Monsters/Equips schema.
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md` — game-owned managed Action producers.
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md` — exact generated Action ABI + isolated proof blueprint.
- `analysis/32_CONFIG_DOMAIN_ATLAS.md` — all Config tables grouped by subsystem/value.
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` — next semantic static-data normalization targets.

`analysis/31_CURRENT_AUTO_TOOL_BRIDGE_INTEGRATION.md` is implementation-adjacent source correlation and is **not default client-research reading**. Open only for that specific integration question.

## Older-tool donor / orchestration

- `analysis/23_AUTOBUFF_V131_SOURCE_DONOR.md` — old-source behavior donor, not canonical mutation architecture.
- `features/AUTO_ORCHESTRATOR.md` — coordinated Train/Party/Buff/Sell/Revive/spot switching design.

---

# Database navigation

Start with:

- `database/SUBSYSTEM_SOURCE_MAP.md` — where each subsystem truth lives.
- `database/FINDING_TO_DOC_MAP.md` — conclusion -> doc.
- `database/FACTS_README.md`
- `database/FACTS.jsonl` — exact atomic facts.
- `database/README.md` — database inventory.

High-value databases:

- `database/MAPS.csv` — 193 maps.
- `database/npcs/NPCS_*.csv` — 1,003 NPCs.
- `database/NPC_SERVICE_CANDIDATES.md`.
- `database/FUBEN_SCENARIOS.csv`.
- `database/AUTOPATH_PORTAL_EDGES.csv` — 165 portal edges.
- `database/AUTOPATH_ITEM_DESTINATIONS.csv` — 23 item destinations.
- `database/autopath_npc/AUTOPATH_NPC_EDGES_*.csv` — 506 NPC-mediated transitions.
- `database/PACKET_IDS.csv` — 169 packet constants.
- `database/PACKET_CATALOG.md`.
- `database/API_QUICK_REFERENCE.md`.
- `database/UI_LAYOUT_CALLBACKS.md`.
- `database/LUA_SCRIPT_CATALOG.md`.
- `database/UI_PACKET_LIFECYCLE.md`.
- `database/AUTO_SETTINGS_SCHEMA.md`.
- `database/NGAMY_SUPPORT_SKILLS.md`.
- `database/CONFIG_TABLE_CATALOG.md` — exact 75-table catalog.
- `database/static/README.md` — intended large normalized Config DB layout.

Large Items/Skills/Magic/Monsters/Equips/Pets/etc. data must be query-oriented. Locate ID/category/index first; do not load all rows into context.

---

# Feature specs

- `features/AUTO_TRAIN.md`
- `features/AUTO_BUFF.md`
- `features/AUTO_SELL.md`
- `features/AUTO_REVIVE.md`
- `features/AUTO_HEAL_NPC.md`
- `features/AUTO_ORCHESTRATOR.md`.

---

# High-value exact facts

## Auto Train

`C_AutoModel.Train = 1`.

Semantic start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

The visible `Đánh quái` settings tab is not the Train start action.

## Nearby peaceful players

`Game.GetNearByPeacePlayers(limit)` supplies:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

Do not restart with CE HP scans for those fields.

## Nga My skill identity correction

- 406 = Phật Quang Phổ Chiếu
- **407 = Xung Hư Dưỡng Khí**
- 408 = Khởi Tử Hồi Sinh
- **423 = Kim Châm Độ Kiếp**
- 424 = Thanh Tâm Phổ Thiện Chú.

Legacy Lua name `KIMCHAMDOKIEP` pointing to 407 is misleading.

## Auto Sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload:

`itemInstanceID:NpcShopID:ShopID`.

One current instance -> one sell -> wait server/item proof -> rescan.

## Storage move

`CMD_ITEM_ACTION = 100005`, Move = `5`.

Payload:

`5:itemInstanceID:destinationSite`.

Bag=10; Storage=11..15.

## Revive / Đầu thai

`CMD_REVIVE_DATA = 200063`

- normal/Đầu thai = 1
- newbie = 2
- skill revive = 3.

## Dynamic NPC dialog

`Selections[selectionID] = visibleText`.

Submit via `CMD_SHOW_GAMEDIALOG = 100007`:

`selectionID:SelectedItemID`.

Usually `SelectedItemID=-1` when no reward item selection is involved.

## Lâu Lan healer candidate

Map 5 = Lâu Lan.

- NPC 337 Đỗ Bất Đằng — `LangZhong1`
- NPC 338 Đỗ Hoàng Đằng — `LangZhong1`
- NPC 339 Đỗ Thanh Đằng — `LangZhong1`.

NPC 339 is a strong static healer candidate. Exact Trị liệu selection remains server/runtime data.

## Weapon classification

In `Equips.xml`, `EquipPoint=0` is Weapon.

Do not classify weapons only as `Type<10`; additional weapon forms exist outside that subtype range.

## Static Config scale

Important exact row counts:

- Skills 2,091
- SkillProperties 2,044
- AutoSkills 300
- Items 5,238
- Equips 22,763
- Medicines 692
- Monsters 17,121
- Tasks 516
- Pets 8,349
- Spirits 1,889
- GrowPoints 407
- Factions 17.

Use `analysis/32_CONFIG_DOMAIN_ATLAS.md` before deciding which dataset to open.

---

# Architecture guardrail

Canonical production direction:

`Resolver -> read-only Scanner -> Snapshot Store -> Observer -> State Machine -> Safety Guard -> Action Queue(max 1 mutable action) -> valid System.Action -> MainThread.Execute -> semantic Game/Lua/UI action -> state proof`

Do not use:

- production continuous `CreateRemoteThread` gameplay worker;
- arbitrary-thread direct Unity/Lua mutation;
- stale UIButton pointers;
- screen coordinates when semantic API exists;
- fixed Sleep as success proof;
- response handlers as requests;
- hardcoded RVA as sole identity;
- OCR/CE when structured game data exists;
- invented NPC coordinates instead of `Game.GetNPCPosition`;
- invented treatment selection IDs;
- automated Captcha solving/bypass.

---

# Current research priorities

Broad reverse is no longer the main job.

Highest-value remaining **knowledge/data** work:

1. normalize/query-index `Skills + SkillProperties + AutoSkills + Factions + Books`;
2. normalize/query-index `Items + Equips + Medicines` and equipment support tables;
3. normalize `Tasks + GrowPoints + GuildTask/Activities`;
4. normalize `Pets + PetFeatures + Spirits + companion equipment`;
5. extract/index `Translations.unity3d` only if localization/semantic text matching needs it;
6. inventory `data.unity3d` only when a concrete missing asset/path/world question requires it;
7. keep runtime-only questions (NPC Trị liệu selection, non-team beneficial-skill acceptance, exact remaining actor fields) as targeted proof, not broad binary reverse.

Read `research/TODO.md`, `research/PROBABLE.md` and `research/HYPOTHESES.md` only when the needed fact is not already VERIFIED.
