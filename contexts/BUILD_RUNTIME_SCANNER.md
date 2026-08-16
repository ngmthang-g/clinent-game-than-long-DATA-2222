# Context Pack — Build Runtime Scanner

## Scope

Use for read-only local-player, nearby-player, team, target, NPC, monster, loot, map, bag, buff and cooldown snapshots.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`
4. `database/AUTO_TOOL_API_CATALOG.md`

The snapshot contract is intentionally the main implementation document. Do **not** preload every subsystem analysis file unless an exact field/evidence question requires it.

## SOURCE DETAIL — open only when needed

- Nearby players / selected target / local RoleData: `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- Map / movement / map objects: `analysis/22_MAP_MINIMAP_RUNTIME.md`
- Bag / NPCShop / item events: `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- Local buff schema/events: `analysis/17_BUFF_RUNTIME_SCHEMA.md`
- Skill cooldown / learned-skill guards: `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- Team: `analysis/25_TEAM_RUNTIME_FOLLOW.md`
- Loot: `analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`
- Pet/Spirit: `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md` only if that feature is requested
- Quest: `analysis/23_TASK_QUEST_AUTOMATION.md` only if that feature is requested
- Static template lookups: exact database record/chunk only when a live ID needs interpretation.

## VERIFIED semantic sources

Local: `Game.RoleData` plus semantic role queries.

Nearby peaceful: `Game.GetNearByPeacePlayers(limit)`.

Train targets: `Game.GetNearbySpritesWithPredicate(...)`.

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

Use semantic identities:

- player/object -> RoleID;
- monster template -> ResID where applicable;
- bag item -> live `ID` plus template `ItemID`;
- skill -> SkillID;
- buff -> BuffID.

Attach timestamp/version/world-generation metadata so feature state machines can reject stale candidates before mutation.

## Important schema boundaries

Do not invent fields just because they would be convenient.

Already VERIFIED for arbitrary nearby PeacePlayer:

`RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID, TeamRank`.

Generic PeacePlayer Position/death is not yet proven by that exact API; resolve only if the chosen Auto Buff implementation truly requires it.

Built-in Train discovery already proves target:

`Type, IsDeath, RoleID, ResID, Position`.

Exact current HP/MaxHP of every unselected monster is not required for basic Train and should not trigger broad reverse unless a concrete policy needs it.

## AOI rule

Nearby APIs expose entities replicated/known to the current client. They do not imply whole-map/server visibility.

## Per-PID rule

Every process has an independent:

```text
SnapshotVersion
WorldGeneration
LocalRole
NearbyPlayers
Targets
Map
Bag
Buffs
Cooldowns
Team
Dialog/Shop/Revival transaction state
```

Static template databases may be shared read-only; live state may not.

## Do not regress to

- CE HP-value search for fields already exposed by semantic APIs;
- OCR of player names/HP bars;
- pixel-based bag inspection;
- one global snapshot shared across multiple PIDs;
- stale object pointers as long-lived identity;
- fake/default Position/death fields where the source schema has not proved them.

## Completion criteria

A scanner is good when it is:

- read-only;
- per-PID;
- typed;
- timestamped/versioned;
- world-generation aware;
- resilient to disappearing objects/map changes;
- event-refreshed where the client exposes events;
- able to publish immutable snapshots that feature state machines consume without touching unstable client objects directly.

Canonical structure and exact field boundaries: `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.