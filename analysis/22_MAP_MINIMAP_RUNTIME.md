# LocalMap / Minimap / WorldMap runtime semantics

Status: **VERIFIED from decrypted `LocalMap_LocalMapTab.lua`, `LocalMap_WorldMapTab.lua`, `Minimap.lua`.**

This is the semantic map/navigation donor for position validation, nearby object display, click-to-move and cross-map Auto navigation.

## `Game.IsMapReady()` is an explicit readiness signal

`Minimap` refuses normal map updates when:

`Game.IsMapReady() == false`.

Nearby-object scanning also runs only when map data exists and `Game.IsMapReady() == true`.

### Tool consequence

Map transition handling should include `Game.IsMapReady()` as a real state guard instead of relying only on a fixed 6-second delay.

A good transition proof is:

```text
expected MapID reached
AND Game.IsMapReady() == true
AND RoleData/Position valid
```

before resuming Train or issuing NPC/item actions.

## Current local map identity / dimensions

The Minimap obtains:

- `Game.GetMapName()`
- `Game.GetMapSize()`
- `Game.RoleData.Position`
- `Game.RoleData.Direction`
- `Game.CameraRotation.y`.

It converts world/grid/minimap coordinates using semantic functions rather than hardcoded screen pixels.

## Static objects on current map

`LocalMap_LocalMapTab` calls:

`Game.GetLocalMapObjects()`.

Each returned object is directly consumed with:

- `objData.Type`
- `objData.Name`
- `objData.Position`.

Verified type strings handled by shipped UI:

- `NPC`
- `Monster`
- `GrowPoint`
- `Zone`
- `Portal`.

The UI groups them by Type and creates location buttons whose `Tag` is the actual world `Position`.

### Tool consequence

For the current map, a semantic location browser/database can be built dynamically from `GetLocalMapObjects()` without image recognition.

It is particularly useful for:

- confirming NPC/portal/monster positions at runtime;
- selecting a destination by object Name/Type;
- cross-checking static Config/AutoPath data.

## Local map click-to-move exact action

Selecting a listed location calls:

`Game.MoveTo(locationWorldPos.X, locationWorldPos.Y)`.

Touching the local map converts UI-local coordinates back to world coordinates and calls:

`Game.MoveTo(worldPos.X, worldPos.Y)`.

So local point navigation has a direct semantic movement API.

## Current move destination

`LocalMap_LocalMapTab:UpdatePositionContinuously()` reads:

`Game.GetCurrentMoveDestination()`.

This provides a real way to display/observe where the game's current movement system is trying to go.

Potential tool use:

- confirm a movement command actually established a destination;
- detect destination changes/cancellation;
- distinguish “not moving because already arrived” from “command never accepted”.

## Team positions on local map

The local map also consumes team data with:

- teammate RoleID
- MapID
- Position

and shows teammates only when their MapID matches the local player's MapID.

This is another example of map/position being semantic game state, not visual inference.

## Nearby dynamic/visible map objects

`Minimap:DoScanObjectsAroundContinuously()` calls every 0.5 seconds:

`Game.GetNearbyObjects()`.

The result is dictionary-like and entries are directly accessed as:

- `.Position`
- `.Type`
- `.Name` for NPC/Portal.

The UI maintains icon state keyed by the returned object dictionary keys and removes icons when a key disappears from the fresh nearby-object result.

### Tool consequence

This is a second world-object source complementary to:

- `GetNearbySpritesWithPredicate`
- `GetNearByPeacePlayers`
- `GetNearByEnemies`
- `GetNearestNPC`
- `GetLocalMapObjects`.

Use the API best matched to the feature rather than broad heap scanning.

## World map data / cross-map route

`LocalMap_WorldMapTab` reads:

`Loader.WorldMapData.Locations`.

Each location object exposes at least:

- `MapID`
- `Name`
- `Description`
- `Icon`
- `PosX`
- `PosY`
- `AllowQuickPath`.

If `AllowQuickPath == true`, the stock UI allows navigation and calls:

`Game.GoTo(SelectedMapID, -1, -1)`.

This confirms the `-1,-1` convention is the normal built-in cross-map destination semantics.

## Choosing between MoveTo and GoTo

Use:

- `Game.MoveTo(X,Y)` for straightforward movement on current map when no cross-map route is needed;
- `Game.GoTo(MapID,X,Y)` / `GoToNPC` for route-aware navigation, especially across maps/portals.

Do not implement custom portal/path logic unless the built-in GoTo path cannot satisfy the concrete feature.

## Wrong-position recovery for Auto Train

A robust version of the requested “sai tọa độ -> tắt Auto -> chạy về -> bật lại” can be:

```text
read RoleData.MapID + Position
 -> compare with saved TrainPoint + tolerance
 -> if wrong:
      StartAutoFight(None)
      wait mutable combat action stopped
      Game.GoTo(savedMap,savedX,savedY)
      wait MapID expected
      wait Game.IsMapReady()==true
      wait distance(Position,TrainPoint)<=tolerance
      StartAutoFight(Train)
```

Do not simply send movement while the Train coroutine is still fighting/chasing another target.

## Position scale caution

Different APIs/data files may express grid/cell/world coordinates differently. The shipped UI uses explicit conversions such as:

- `Game.WorldToGridPosition`
- LocalMap `WorldToLocalMapPosition`
- `LocalMapToWorldPosition`.

Future AI should not assume a static Config X/Y uses the same unit as a live world `Position` without checking the source/API.

## State-proof hierarchy for map movement

1. target `RoleData.MapID` / current map state;
2. `Game.IsMapReady()`;
3. fresh valid `RoleData.Position`;
4. distance to intended final point;
5. `GetCurrentMoveDestination()` when diagnosing movement state;
6. timeouts only as failure guards.
