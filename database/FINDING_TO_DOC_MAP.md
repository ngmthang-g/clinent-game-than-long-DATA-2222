# Finding → document map

Use this file when you remember a conclusion but do not know where it was stored. It maps high-value findings/questions to the canonical document that explains them.

## AI navigation first

| Need | Canonical entry |
|---|---|
| Start without reading whole repo | `AI_BOOTSTRAP.md` |
| Route build task to smallest reading set | `AI_ROUTER.md` |
| Know which source layer owns a subsystem truth | `database/SUBSYSTEM_SOURCE_MAP.md` |
| Task-specific required/optional docs | `contexts/BUILD_*.md` |
| Fast exact constants/IDs/facts | `database/FACTS.jsonl` |
| How knowledge/evidence is preserved | `KB_METHOD.md` |

## Deep technical map

| Finding / question | Canonical document |
|---|---|
| Client architecture, file priority | `analysis/00_MASTER_RESEARCH_MAP.md` |
| IL2CPP metadata/runtime surface | `analysis/01_IL2CPP_RUNTIME_METADATA.md` |
| Lua/Game/GUI/Network bridge | `analysis/02_LUA_GAME_UI_NETWORK_API.md` |
| World/entity/map/path classes | `analysis/03_WORLD_ENTITY_MAP_PATH.md` |
| Inventory/item/shop foundation | `analysis/04_INVENTORY_ITEMS_SHOP.md` |
| Combat/skills/buffs foundation | `analysis/05_COMBAT_SKILLS_BUFFS.md` |
| FG decrypt/custom Unity bundles | `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` |
| Launcher/support modules | `analysis/07_SUPPORT_MODULES_LAUNCHER.md` |
| Every major client file and current reverse value | `analysis/08_FILE_BY_FILE_CATALOG.md` |
| Decrypted Config/Interface/Lua breakthrough | `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md` |
| Built-in Train/PK/Quest/FuBen auto engine | `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` |
| Exact packet/action payloads | `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md` |
| `GoToNPC`, `GoToMonster`, global helpers | `analysis/12_GLOBAL_LUA_HELPERS.md` |
| UI event/runtime action surface | `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` |
| Nearby peaceful/enemy player schema, SelectedTarget | `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` |
| Nga My recovery donor and corrected skill identity | `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` |
| Other-player/social interaction data | `analysis/16_PLAYER_INTERACTION_UI_API.md` |
| BuffID/duration/stack/properties/events | `analysis/17_BUFF_RUNTIME_SCHEMA.md` |
| Skill cooldown, QuickSkills, F-key semantics | `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md` |
| Progress/channel/Captcha safety | `analysis/19_PROGRESS_CAPTCHA_SAFETY.md` |
| Bag grid, item events, NPCShop and Quick Sell | `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md` |
| MainThread exact queue/Update/Action.Invoke chain | `analysis/21_MAIN_THREAD_DISPATCHER.md` |
| Map-ready/minimap/local-object/movement state | `analysis/22_MAP_MINIMAP_RUNTIME.md` |
| Task schema and built-in Auto Quest | `analysis/23_TASK_QUEST_AUTOMATION.md` |
| Pet/Spirit state and auto behavior | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` |
| Team member HP/position/actions and Follow mode | `analysis/25_TEAM_RUNTIME_FOLLOW.md` |
| Storage item move / bank money semantics | `analysis/26_STORAGE_BANK_ITEM_MOVE.md` |
| Ground loot/item-pack scan/filter/pickup | `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md` |
| Items/Skills/Magic/Monsters/Equips normalized schema | `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` |
| Game-owned producers constructing Action + MainThread.Execute | `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md` |
| Generated Action constructor ABI / external proof blueprint | `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md` |
| All 75 Config tables grouped by subsystem and reverse value | `analysis/32_CONFIG_DOMAIN_ATLAS.md` |
| Highest-value Config data still worth normalizing | `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Full map/NPC/route lookup | `database/README.md` + CSVs |
| Which runtime/Lua/Config/protocol source to use for a subsystem | `database/SUBSYSTEM_SOURCE_MAP.md` |
| All 75 Config table names/counts | `database/CONFIG_TABLE_CATALOG.md` |
| Planned/query-oriented static DB layout | `database/static/README.md` |
| All 169 packet constants | `database/PACKET_IDS.csv` |
| Network evidence levels / solved vs unsolved request paths | `database/NETWORK_COMMAND_CATALOG.md` |
| High-value API/runtime symbols | `database/API_QUICK_REFERENCE.md` |
| UI layout/callback catalog | `database/UI_LAYOUT_CALLBACKS.md` |
| High-value Lua script catalog | `database/LUA_SCRIPT_CATALOG.md` |
| UI/server packet lifecycle | `database/UI_PACKET_LIFECYCLE.md` |
| Nga My support skill truth table | `database/NGAMY_SUPPORT_SKILLS.md` |
| Auto settings schema | `database/AUTO_SETTINGS_SCHEMA.md` |
| NPC service candidates by Name/ResName | `database/NPC_SERVICE_CANDIDATES.md` |
| Auto Train feature design | `features/AUTO_TRAIN.md` |
| Auto Buff nearby-player design | `features/AUTO_BUFF.md` |
| Auto Sell design | `features/AUTO_SELL.md` |
| Auto Revive/Đầu thai | `features/AUTO_REVIVE.md` |
| NPC Trị liệu mechanism | `features/AUTO_HEAL_NPC.md` |
| Adaptive cross-feature orchestration | `features/AUTO_ORCHESTRATOR.md` |
| Evidence/preservation method | `KB_METHOD.md` |

## Static-data routing shortcuts

| Question | Read first |
|---|---|
| “Which Config table probably answers this?” | `analysis/32_CONFIG_DOMAIN_ATLAS.md` |
| “What Config tables still need full indexes/chunks?” | `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Skill/faction/book/automatic trigger semantics | `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Item/equip/medicine policy | `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` + `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Task/gather data | `analysis/23_TASK_QUEST_AUTOMATION.md` + `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Pet/Spirit template intelligence | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` + `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` |
| Cosmetics/model/FX tables | `analysis/32_CONFIG_DOMAIN_ATLAS.md` only unless a concrete feature needs deeper extraction |

## Build routing map

| Build problem | Context pack |
|---|---|
| Core architecture / multi-client / action gate | `contexts/BUILD_TOOL_CORE.md` |
| Runtime scanners/snapshots | `contexts/BUILD_RUNTIME_SCANNER.md` |
| External System.Action / MainThread bridge | `contexts/BUILD_MAINTHREAD_BRIDGE.md` |
| Auto Train | `contexts/BUILD_AUTO_TRAIN.md` |
| Auto Buff | `contexts/BUILD_AUTO_BUFF.md` |
| Auto Sell | `contexts/BUILD_AUTO_SELL.md` |
| NPC treatment | `contexts/BUILD_AUTO_HEAL.md` |
| Revive | `contexts/BUILD_AUTO_REVIVE.md` |
| Party/team/follow | `contexts/BUILD_PARTY.md` |
| Combined adaptive automation | `contexts/BUILD_ORCHESTRATOR.md` |

## Exact facts that should be easy to find

- Nearby peaceful player records expose `RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank` → `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` / `FACTS.jsonl`.
- Train semantic start is `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)` → `analysis/10...` / `features/AUTO_TRAIN.md`.
- Shop sell request is packet `200036`, payload `itemInstanceID:NpcShopID:ShopID` → `analysis/11...` / `analysis/20...`.
- Đầu thai is revive packet `200063` value `1` → `features/AUTO_REVIVE.md`.
- NPC dialog uses runtime `Selections[selectionID]=visibleText`, submit packet `100007` → `analysis/11...` / `features/AUTO_HEAL_NPC.md`.
- Lâu Lan NPC `339` = Đỗ Thanh Đằng, `LangZhong1` → `database/npcs/` / `database/NPC_SERVICE_CANDIDATES.md`.
- Local buffs expose `BuffID, DurationTick, Stack` → `analysis/17...`.
- Skill cooldown is semantic; physical F1/F2 is not skill identity → `analysis/18...`.
- 407 is Xung Hư Dưỡng Khí; actual Kim Châm Độ Kiếp is 423 → `analysis/15...` / `database/NGAMY_SUPPORT_SKILLS.md`.
- MainThread dispatcher: `.ctor` creates queue at `this+0x20`; `Execute` enqueues; `Update` calls `DoExecuteWorks`; dequeued Action is invoked → `analysis/21...`.
- TCPGame/TCPLogin handlers construct legitimate `System.Action` objects and call `MainThread.Execute` → `analysis/29...`.
- Generated Action constructor ABI uses Action object + target/null + callback MethodInfo* → `analysis/30...`.
- Team state exposes structured member RoleID/Name/Level/Faction/Map/HP/MaxHP/backup X/Y; Follow uses nearby position then cross-map fallback → `analysis/25...`.
- Storage movement uses `CMD_ITEM_ACTION=100005`, action `5`, payload `5:instanceID:destinationSite` → `analysis/26...`.
- Loot engine uses nearby ItemPack RoleID/Position + semantic path/move/click/pickup APIs → `analysis/27...`.
- Static Weapon identity is `EquipPoint=0`, not merely Equip subtype `Type<10` → `analysis/28...`.
- Config is **75 verified extracted XML tables**, not a prediction → `research/VERIFIED_PHASE2.md` / `analysis/32...`.
- Interface is **339 Lua classes + 338 layouts + 1,469 bindings**, not a prediction → `research/VERIFIED_PHASE2.md` / `database/LUA_SCRIPT_CATALOG.md`.

## Rule

When a new discovery materially changes retrieval, update this map. Do not duplicate every detail from the target document; this file is a router, not another knowledge dump.
