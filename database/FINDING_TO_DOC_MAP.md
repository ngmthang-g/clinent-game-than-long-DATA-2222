# Finding → document map

Use this file when you remember a conclusion but do not know where it was stored. It maps high-value findings to the canonical document that explains them.

| Finding / question | Canonical document |
|---|---|
| Client architecture, file priority | `analysis/00_MASTER_RESEARCH_MAP.md` |
| IL2CPP metadata/runtime surface | `analysis/01_IL2CPP_RUNTIME_METADATA.md` |
| Lua/Game/GUI/Network bridge | `analysis/02_LUA_GAME_UI_NETWORK_API.md` |
| World/entity/map/path classes | `analysis/03_WORLD_ENTITY_MAP_PATH.md` |
| Inventory/item/shop semantics | `analysis/04_INVENTORY_ITEMS_SHOP.md` |
| Combat/skills/buffs | `analysis/05_COMBAT_SKILLS_BUFFS.md` |
| FG decrypt/custom Unity bundles | `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` |
| Launcher/support modules | `analysis/07_SUPPORT_MODULES_LAUNCHER.md` |
| Every major client file and reverse value | `analysis/08_FILE_BY_FILE_CATALOG.md` |
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
| `FGStudio.Engine.Utilities.MainThread` dispatcher | `analysis/21_MAIN_THREAD_DISPATCHER.md` |
| Map-ready/minimap/local-object/movement state | `analysis/22_MAP_MINIMAP_RUNTIME.md` |
| Task schema and built-in Auto Quest | `analysis/23_TASK_QUEST_AUTOMATION.md` |
| Pet/Spirit state and auto behavior | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` |
| Full map/NPC/route lookup | `database/README.md` + CSVs |
| All packet constants | `database/PACKET_IDS.csv` |
| UI layout/callback catalog | `database/UI_LAYOUT_CALLBACKS.md` |
| High-value Lua script catalog | `database/LUA_SCRIPT_CATALOG.md` |
| UI/server packet lifecycle | `database/UI_PACKET_LIFECYCLE.md` |
| Nga My support skill truth table | `database/NGAMY_SUPPORT_SKILLS.md` |
| Auto settings schema | `database/AUTO_SETTINGS_SCHEMA.md` |
| Auto Train feature design | `features/AUTO_TRAIN.md` |
| Auto Buff nearby-player design | `features/AUTO_BUFF.md` |
| Auto Sell design | `features/AUTO_SELL.md` |
| Auto Revive/Đầu thai | `features/AUTO_REVIVE.md` |
| NPC Trị liệu mechanism | `features/AUTO_HEAL_NPC.md` |
| Evidence/preservation method | `KB_METHOD.md` |

## Exact facts that should be easy to find

- Nearby peaceful player records expose `RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank` → `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`.
- Train semantic start is `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)` → `analysis/10...` / `features/AUTO_TRAIN.md`.
- Shop sell request is packet `200036`, payload `itemInstanceID:NpcShopID:ShopID` → `analysis/11...` / `analysis/20...`.
- Đầu thai is revive packet `200063` value `1` → `features/AUTO_REVIVE.md`.
- NPC dialog uses runtime `Selections[selectionID]=visibleText`, submit packet `100007` → `analysis/11...` / `features/AUTO_HEAL_NPC.md`.
- Lâu Lan NPC `339` = Đỗ Thanh Đằng, `LangZhong1` → `database/npcs/` / `database/NPC_SERVICE_CANDIDATES.md`.
- Local buffs expose `BuffID, DurationTick, Stack` → `analysis/17...`.
- Skill cooldown is semantic; physical F1/F2 is not skill identity → `analysis/18...`.
- 407 is Xung Hư Dưỡng Khí; real Kim Châm Độ Kiếp is 423 → `analysis/15...` / `database/NGAMY_SUPPORT_SKILLS.md`.
- Main-thread bridge candidate is `FGStudio.Engine.Utilities.MainThread` with `Execute(Action)` + queue → `analysis/21...`.

## Rule

When a new discovery is added, update this map only if it materially helps future retrieval. Do not turn it into a duplicate copy of every document.
