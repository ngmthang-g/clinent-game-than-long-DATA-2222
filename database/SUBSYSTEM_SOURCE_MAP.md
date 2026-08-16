# Subsystem Source Map — where AI should look first

Status: **routing/index document synthesized from VERIFIED client KB.**

Purpose: when a feature/question names a gameplay subsystem, this file tells AI which source layer is most valuable first. It prevents broad reverse-engineering and prevents static Config, Lua, runtime state and packet semantics from being mixed together.

General order:

`semantic runtime/Lua source -> Config/static DB -> exact UI/layout binding -> exact packet/action -> native disassembly only if still missing`

---

| Subsystem / task | Primary runtime/API source | Primary Lua/UI source | Static Config / DB | Exact action/protocol source | Canonical deep docs |
|---|---|---|---|---|---|
| Local role identity/vitals | `LuaSystemSharedData.get_LeaderRoleData`, role getters | shipped HUD/role UI | faction/default character tables only for template context | server sync events | `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`, `analysis/22_MAP_MINIMAP_RUNTIME.md` |
| Nearby peaceful players | `Game.GetNearByPeacePlayers(limit)` | nearby/social UI | `Factions`, visual/avatar tables for interpretation | target/social actions only when needed | `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`, `analysis/16_PLAYER_INTERACTION_UI_API.md` |
| Nearby enemies/targets | `GetNearByEnemies`, `SelectedTarget`, `SelectTarget`, `ChaseTarget` | AutoFight / nearby target UI | `Monsters`, `Skills` | combat request path | `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`, `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` |
| Map / movement | `IsMapReady`, `GetLocalMapObjects`, `GetNearbyObjects`, `MoveTo`, `GoTo`, `HasPath` | `Global_Functions`, AutoFight helpers | `Maps`, `WorldMap`, `AutoPath` | movement/map commands only if semantic call insufficient | `analysis/03_WORLD_ENTITY_MAP_PATH.md`, `analysis/12_GLOBAL_LUA_HELPERS.md`, `analysis/22_MAP_MINIMAP_RUNTIME.md` |
| NPC identity/navigation | `GetNPCPosition`, `ClickNPC`, `GetNearestNPC` | `GoToNPC` helper, `GameDialog` | `NPCs`, `AutoPath`, `MAPS.csv` | click/dialog packets | `analysis/12_GLOBAL_LUA_HELPERS.md`, `features/AUTO_HEAL_NPC.md` |
| NPC service/dialog | active `GameDialogData.Selections` | `GameDialog.lua`, `GameDialog_Layout` | NPC identity only; service may be heuristic | `CMD_SHOW_GAMEDIALOG=100007`, payload `selectionID:SelectedItemID` | `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`, `features/AUTO_HEAL_NPC.md` |
| Auto Train | AutoFight semantic state, world/target/skill APIs | `AutoFight_Main`, `AutoTrainMonster`, `AutoFight_Layout` | `Monsters`, `Skills`, `AutoSkills` | semantic wrapper preferred over raw packet | `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`, `features/AUTO_TRAIN.md` |
| Skill identity/use | `GetAbilities`, `CanUseSkill`, `GetSkillCooldown`, `UseSkill` | SkillBar / AutoHp / AutoFight | `Skills`, `SkillProperties`, `Books`, `Factions`, `AutoSkills` | skill request only if wrapper semantics insufficient | `analysis/05_COMBAT_SKILLS_BUFFS.md`, `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md` |
| Buff state | `GetBuffs`, `GetBuffData`, `GetBuffProperties`, `HasBuff` | AutoHp / buff UI | `MagicAtrributes`, skill/property tables | buff add/update/remove are mostly server events; do not treat response as request | `analysis/17_BUFF_RUNTIME_SCHEMA.md` |
| Nga My / Auto Buff | nearby peaceful-player API + skill APIs | `AutoHp`, `Utilities` | `Skills`, `SkillProperties`, `Factions`, support-skill lookup | semantic `SelectTarget`/`UseSkill` on valid main-thread action path | `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`, `features/AUTO_BUFF.md`, `database/NGAMY_SUPPORT_SKILLS.md` |
| Bag/inventory | `GetItemsAtSite`, `GetItemData`, `GetFreeBagSpace`, `GetItemType`, `GetEquipType`, sellability APIs | `BagItemsGrid`, `RoleInfo_BagTab` | `Items`, `Equips`, `Medicines`, `Gems`, equip support tables | `CMD_ITEM_ACTION`, bag sort, shop requests | `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`, `analysis/04_INVENTORY_ITEMS_SHOP.md` |
| Auto Sell | live bag instance + `IsItemSellable` | `NPCShop_SellItemTab`, quick-sell UI | `Items`, `Equips`; static policy only | `CMD_NPC_SHOP_SELL_REQUEST=200036`, `itemInstanceID:NpcShopID:ShopID` | `features/AUTO_SELL.md`, `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md` |
| Storage / bank | `GetItemsAtSite(site)` + live item instances | `Storage.lua` | items/equips only for policy | `CMD_ITEM_ACTION=100005`, move `5:instanceID:destinationSite`; bank feature actions | `analysis/26_STORAGE_BANK_ITEM_MOVE.md` |
| Ground loot | `GetNearbyItemPack`, `HasPath`, `MoveToEx`, `ClickToObject`, `PickUpItemFromItemPack` | `AutoFight_Main`, `PickUp` | `Items`, `Equips`, `Gems` for filtering | semantic pickup API preferred | `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md` |
| Revive / death recovery | local death/life state | `Revival`, AutoFight/AutoHp death handling | no static table required for core action | `CMD_REVIVE_DATA=200063`; normal=1/newbie=2/skill=3 | `features/AUTO_REVIVE.md` |
| Team / party | `C_TeamData`, `GetNearTeammates`, `GetNearbyTeamLeaders` | `TeamRole`, `TeamInvite`, `AutoFight_Main` follow | faction/avatar tables only for interpretation | `CMD_TEAM_ACTION`, verified action values/payloads | `analysis/25_TEAM_RUNTIME_FOLLOW.md`, `contexts/BUILD_PARTY.md` |
| Task / quest | current task state/events | task UI + built-in `AutoMainQuest` | `Tasks`, `NPCs`, `Monsters`, `GrowPoints`, `Maps`, `AutoPath` | assign/update/remove task events; action depends objective | `analysis/23_TASK_QUEST_AUTOMATION.md` |
| FuBen / dungeon | map/world/target/task runtime | `AutoFight_FuBen` | `FuBenScenarios`, `Maps`, `NPCs`, `Monsters` | scenario-specific actions | `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`, `database/FUBEN_SCENARIOS.csv` |
| Pet | current Pet object/state, skill/use APIs | pet UI / AutoFight pet logic | `Pets`, `PetFeatures`, `PetEquips`, `PetEquipSets` | `CMD_PET_ACTION` where exact payload is documented | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` |
| Spirit | current Spirit object/state | AutoFight Spirit logic | `Spirits`, `SpiritFeatures` | Spirit action packet where documented | `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` |
| Guild | current role/guild state when available | guild UI/Lua scripts | `GuildConfig`, `GuildTask`, `RoleReputes` | guild packets only after exact Lua trace | `analysis/32_CONFIG_DOMAIN_ATLAS.md` + targeted future trace |
| Gather/life skill | nearby world objects + path APIs | task/gather UI when applicable | `GrowPoints`, `Tasks`, `Maps` | object interaction semantics | `analysis/03_WORLD_ENTITY_MAP_PATH.md`, `analysis/32_CONFIG_DOMAIN_ATLAS.md` |
| Faction/skill-tree interpretation | live FactionID + abilities | faction/skill UI | `Factions`, `Books`, `BookLevelUpCost`, `Skills` | usually no direct mutation required for lookup | `analysis/32_CONFIG_DOMAIN_ATLAS.md` |
| Equipment classification | `GetItemType`, `GetEquipType`, live item data | Bag/equip UI | `Equips`, `Items`, `EquipSets`, identify/enhance/extended attribute tables | live instance mutations only | `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` |
| PC hotkeys | semantic action should still be preferred | input/UI binding layer | `PCInputKeyBinding` | keyboard simulation should be fallback only | `analysis/32_CONFIG_DOMAIN_ATLAS.md` |
| Captcha | Captcha event/UI | Captcha UI | none | user/manual answer path only | `analysis/19_PROGRESS_CAPTCHA_SAFETY.md` |
| Main-thread action execution | game-owned `MainThread.Execute(Action)` | not a UI feature | none | managed Action -> queue -> Update -> invoke | `analysis/21_MAIN_THREAD_DISPATCHER.md`, `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`, `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md` |

---

## Source authority by question type

### “What is ID X?”

Prefer static database/config.

Examples:

- MapID -> `MAPS.csv`
- NPCID -> `database/npcs/`
- SkillID -> normalized `Skills` when available / support skill DB
- ItemID -> normalized `Items` when available
- MonsterID -> normalized `Monsters` when available.

### “What exists right now around the player?”

Use runtime semantic APIs, not Config.

Static tables cannot tell whether an object is currently spawned/in range/alive.

### “What button/action does this UI perform?”

Read layout binding -> same-name Lua script -> actual semantic call/packet.

Do not stop at visible button text.

### “What packet should be sent?”

Only use exact payloads recovered from Lua/native request paths.

Packet-name existence alone is insufficient.

### “Did the action succeed?”

Use fresh runtime/server-authoritative state or event proof.

A fixed delay is only a timeout guard, never proof.

---

## AI anti-overread rule

For a normal subsystem task:

1. find the row in this file;
2. open the primary runtime/Lua/static source listed;
3. open at most the canonical deep docs named in that row;
4. query exact IDs from database;
5. reverse native only if an exact missing contract remains.

Do not preload every Config table just because 75 exist.
