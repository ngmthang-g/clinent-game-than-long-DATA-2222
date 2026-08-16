# World / Entity / Map / Pathfinding — current semantic model

> Phase 2/3 solved several questions that were still predictions in the original version of this file. This refresh separates VERIFIED runtime/static data from the few actor/path questions that remain targeted research.

---

## 1. Core conclusion

The client already exposes two strong world layers:

1. **semantic query/state layer** through `LuaSystemSharedData` / `LuaSystemAPI_Game`;
2. **scene/native layer** through `FGStudio.Engine.Objects.GScene`, pathfinder/grid/object classes.

Static Config additionally provides maps/NPCs/monsters/routes/scenarios.

Therefore a robust world scanner/navigation system should prefer:

```text
static DB for template identity/topology
 + runtime SharedData/Game APIs for what exists now
 + GScene/native only for exact missing engine-level state
```

not broad process-memory heuristics.

---

## 2. `LuaSystemSharedData` — runtime world query layer

High-value query names:

- `GetNearestNPC`
- `GetNearbySprites`
- `GetNearbyTeamLeaders`
- `GetNearTeammates`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetNearestItemPack`
- `GetNearbyItemPack`
- `get_LeaderRoleData`.

Related world-data names include:

- `npcData`
- `monsterData`
- `petData`
- `growPointData`
- `portalData`
- `zoneData`.

### Already VERIFIED through shipped UI/Lua

#### Nearby peaceful players

`GetNearByPeacePlayers(limit)` supplies at least:

- RoleID
- Name
- Level
- FactionID
- HP
- MaxHP
- GuildName
- AvartaID
- TeamRank.

#### Nearby enemies

Shipped enemy UI reads the same core identity/vital fields.

#### Team members

Structured team state gives:

- RoleID
- RoleName
- Level
- FactionID
- MapID
- Hp
- MaxHp
- AvartaID
- PosX
- PosY.

#### Selected target

`Game.SelectedTarget` exposes a richer target object with identity/type/vital fields; selected-player UI additionally exposes social IDs.

So the old statement “world object schemas are basically unknown” is no longer correct. Only **additional fields or object families not yet consumed by shipped code** remain to be mapped.

---

## 3. AOI / visibility boundary

The client has real semantic data for nearby non-party players, but this does not mean it knows every actor on the entire server/map.

Correct model:

```text
server world
 -> AOI/visibility replication
 -> local client object/data structures
 -> SharedData/Game queries
```

Consequences:

- a nearby player can expose HP/MaxHP without party membership;
- a far-away actor not replicated into the client cannot be read from local runtime just because a static template exists;
- static `Monsters`/`NPCs` databases tell what **can exist**, runtime queries tell what **exists now**.

---

## 4. `GScene` — scene/native world layer

Class:

`FGStudio.Engine.Objects.GScene`

Observed high-value members include:

- `GetGroundHeight`
- `InSafeArea`
- `CanEnter`
- `ScreenToPosition`
- select-target decoration functions
- `DoSyncPosition`
- `DoVisionLogic`
- `DoCheckPetLogic`
- `get_PathFinder`
- role/pet/trap/model load functions.

Related types:

- `PathFinder`
- `NodeGrid`
- `LocalMapComponents`
- `NPCData`
- `MonsterData`
- `GrowPointData`
- `ZoneData`
- `PortalData`
- `MapAreaSoundData`
- `Obstructions`
- `DynamicObstructions`
- `Regions`
- `SafeAreas`.

`ClickNPC` native disassembly calls scene selection logic, confirming GScene participates in gameplay object targeting rather than being only visual rendering code.

### When to use GScene/native

Use only when semantic APIs are insufficient, e.g.:

- precise ground/obstruction/path-grid questions;
- scene object internals not exposed to Lua;
- exact safe-area/enterability behavior.

Do not reverse GScene merely to get information already available from SharedData/Game APIs.

---

## 5. Runtime map / movement API — VERIFIED

Shipped code uses semantic members including:

- `Game.IsMapReady()`
- `Game.GetMapName()`
- `Game.GetMapSize()`
- `Game.GetLocalMapObjects()`
- `Game.GetNearbyObjects()`
- `Game.GetCurrentMoveDestination()`
- `Game.MoveTo(X,Y)`
- `Game.MoveToEx(...)`
- `Game.GoTo(MapID,X,Y,callback)`
- `Game.HasPath(from,to)`
- `Game.GetDistance`
- `Game.GetNPCPosition(npcID)`
- `Game.ClickNPC(npcID)`
- `Game.ClickToObject(objectID)`
- `Game.SelectTarget(RoleID)`
- `Game.ChaseTarget(...)`.

This means movement/navigation is already a high-level semantic subsystem. Physical WASD/mouse navigation should be a fallback, not the default architecture.

---

## 6. Static map database — VERIFIED

`Maps.xml` contains **193 map rows**.

Normalized lookup:

`database/MAPS.csv`.

Typical fields include:

- MapID
- Name
- ResName
- Level
- Type
- ServerID
- music/color-related config.

Example already verified:

`Map 5 = Lâu Lan`, ResName `loulangucheng`, City, level 75.

Static map identity is useful for lookup and routing policy. Runtime `Game.IsMapReady` / current map state remains authoritative for execution.

---

## 7. Static NPC database — VERIFIED

`NPCs.xml` contains **1,003 NPC rows** with at least:

- ID
- Name
- ResName
- Avarta.

`AutoPath/NPCData` provides many NPC -> MapID associations.

Normalized DB:

`database/npcs/NPCS_*.csv`.

Examples:

- NPC 328 Ba Nhĩ -> Map 5 Lâu Lan
- NPC 337 Đỗ Bất Đằng -> `LangZhong1`, Map 5
- NPC 338 Đỗ Hoàng Đằng -> `LangZhong1`, Map 5
- NPC 339 Đỗ Thanh Đằng -> `LangZhong1`, Map 5
- NPC 373 Mã Kiêu Minh -> Map 5.

### Coordinate rule

`AutoPath/NPCData` does **not** provide the normal NPC X/Y used by runtime interaction.

Use:

`Game.GetNPCPosition(npcID)`.

Do not generate fake static coordinates from unrelated fields.

### Service rule

Name/ResName can generate **service candidates** (doctor/vendor/blacksmith/storage), but actual service contract is server/runtime UI state.

Use:

`database/NPC_SERVICE_CANDIDATES.md`.

---

## 8. Built-in NPC navigation — VERIFIED

Global helper flow:

```text
GoToNPC(mapID,npcID)
 -> change map with Game.GoTo(map,-1,-1) if needed
 -> Game.GetNPCPosition(npcID)
 -> Game.GoTo(map,X,Y)
 -> resolve nearest/current NPC
 -> semantic interaction
```

This is more robust than hardcoded per-NPC X/Y in the external tool.

---

## 9. Static AutoPath topology — VERIFIED

`AutoPath.xml` contains 1,618 records overall.

Extracted route databases include:

- **165 direct portal edges** -> `database/AUTOPATH_PORTAL_EDGES.csv`
- **506 NPC-mediated transitions** -> `database/autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- **23 item/destination records** -> `database/AUTOPATH_ITEM_DESTINATIONS.csv`
- NPCData/map associations.

### Use

Good for:

- map adjacency/topology;
- explaining possible route chains;
- route diagnostics/fallback planning.

### Limitation

A static edge may still depend on:

- level;
- quest;
- event;
- current server/state.

Therefore runtime `Game.GoTo` remains preferred executor.

---

## 10. Monster database / runtime monster scanner

Static `Monsters.xml` contains **17,121 rows** with normalized fields covering identity, level, MaxHP, combat stats, AI and skill references.

This gives offline interpretation:

```text
MonsterID
 -> Name / ResName / Level / MaxHP / AI / skills
```

Runtime nearby enemy/sprite/world queries give actual spawned actors in AOI.

Potential reliable scanner model:

```text
runtime object
 -> object/template/RoleID
 -> static Monster row if applicable
 -> current HP/state/position from runtime
```

Do not use static Monster MaxHP as proof of a live actor's current HP/state.

---

## 11. Grow points / gathering

`GrowPoints.xml` contains **407 rows** with gather/life-skill/quest requirement semantics.

This can join task objectives to semantic world object identity.

Potential flow:

```text
current Task objective
 -> GrowPoint template
 -> nearby world object
 -> path/interact
 -> progress/event proof
```

Exact runtime GrowPoint object fields should be mapped only if a concrete gather feature needs them.

---

## 12. Ground item / ItemPack — VERIFIED semantic engine

The old prediction that loot “probably has a semantic representation” is solved.

Built-in Auto pickup uses:

- `Game.GetNearbyItemPack(...)`
- ItemPack `RoleID`
- ItemPack `Position`
- `Game.HasPath`
- `Game.MoveToEx`
- `Game.ClickToObject`
- pack-content response
- `Game.GetFreeBagSpace`
- `Game.PickUpItemFromItemPack`.

Observed pick-all:

`Game.PickUpItemFromItemPack(itemPackID, -1, 1)`.

Canonical detail:

`analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`.

No OCR/pixel loot detection is needed.

---

## 13. PathFinder / NodeGrid — still targeted research

Native symbols strongly suggest a grid/path/obstruction model.

Potential future value:

- offline obstacle/path diagnostics;
- custom route planning;
- map reachability analysis.

But this is **not** currently needed for most automation because `Game.GoTo` / `HasPath` already exist.

Only inspect exact `PathFinder/NodeGrid` data or `data.unity3d` if runtime pathing becomes a real blocker.

Hypothesis is tracked in `research/HYPOTHESES.md`.

---

## 14. Runtime actor fields still worth targeted mapping

Already verified for nearby players/team/selected target: substantial identity/vital/social state.

Still plausible but not automatically verified on every nearby actor record:

- MP/MaxMP;
- precise Position object on every query variant;
- TeamID/GuildID directly on nearby peaceful record;
- current target/chase/combat/PK state;
- richer target buff IDs/durations;
- movement/action/animation state.

Do not guess offsets. Inspect actual return object/class only when a feature needs one of these fields.

---

## 15. State-machine implication

World actions should be proof-driven.

Example cross-map return to train spot:

```text
stop/leave current action
 -> Game.GoTo(targetMap,...)
 -> wait current MapID == expected
 -> wait IsMapReady == true
 -> wait valid position
 -> move to train point
 -> wait distance <= tolerance
 -> resume Train
```

Example death/revive:

```text
Dead
 -> revive state/action available
 -> one revive request
 -> wait alive + map readiness
 -> reacquire current world snapshot
 -> navigate back
 -> resume
```

Fixed delays are failure timeouts only.

---

## 16. Targeted research order from here

Only if a concrete feature needs more:

1. inspect exact runtime class returned by one relevant SharedData query;
2. map only the missing fields;
3. join to existing static Maps/NPCs/Monsters/GrowPoints DB;
4. inspect GScene/PathFinder only if semantic APIs do not solve execution;
5. inspect `data.unity3d` only for an exact asset/path/resource gap.

Do not broad-reverse UnityPlayer/GameAssembly or recreate already-extracted static databases.
