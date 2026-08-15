# Context Pack — Build Runtime Scanner

## Scope

Use for read-only local-player, nearby-player, team, target, NPC, monster, loot, map, bag, buff and cooldown snapshots.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
3. `analysis/22_MAP_MINIMAP_RUNTIME.md`
4. `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
5. `analysis/17_BUFF_RUNTIME_SCHEMA.md`
6. `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`

## OPTIONAL by data type

- Team: `analysis/25_TEAM_RUNTIME_FOLLOW.md`
- Loot: `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`
- Pet/Spirit: `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`
- Quest: `analysis/23_TASK_QUEST_AUTOMATION.md`
- Static template lookups: `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` + specific CSV chunk.

## VERIFIED semantic sources

Local: `Game.RoleData`.

Nearby peaceful: `Game.GetNearByPeacePlayers(limit)`.

Nearby enemies: `Game.GetNearByEnemies(...)`.

Selected target: `Game.SelectedTarget`.

Team: `C_TeamData` + `Game.GetNearTeammates(...)`.

NPC/loot: `Game.GetNearestNPC`, `GetNearbyObjects`, `GetNearestItemPack`, `GetNearbyItemPack`.

Map: `Game.IsMapReady`, `GetLocalMapObjects`, `GetNearbyObjects`, `GetCurrentMoveDestination`.

Bag: `Game.GetItemsAtSite(site)`, `Game.GetFreeBagSpace()`.

Local buffs: `Game.GetBuffs()`.

Skill cooldown: `Game.GetSkillCooldown(skillID)`.

## Snapshot principle

Copy only semantic values needed by the tool into immutable external records. Do not retain Lua/C# object pointers across scans, UI transitions or map transitions.

Suggested player snapshot:

`RoleID, Name, Level, FactionID, GuildName, HP, MaxHP, HPPercent, TeamRank, Position?, IsDeath?, LastSeenTick`.

Suggested item snapshot:

`ID(instance), ItemID(template), Position, Site, Quantity, Bound, type/equip classification, LastSeenTick`.

## AOI rule

Nearby APIs expose entities replicated/known to the current client. They do not imply whole-map/server visibility.

## Do not regress to

- CE HP-value search for fields already exposed by semantic APIs;
- OCR of player names/HP bars;
- pixel-based bag inspection;
- one global snapshot shared across multiple PIDs;
- stale object pointers as long-lived identity.

## Completion criteria

A scanner is good when it is read-only, per-PID, typed, timestamped, resilient to disappearing objects/map changes, and publishes immutable snapshots that feature state machines can consume without touching unstable client objects directly.