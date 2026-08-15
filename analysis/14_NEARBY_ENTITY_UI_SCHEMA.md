# Nearby entity / target schema recovered from UI Lua

Status: **VERIFIED for the fields explicitly accessed by the shipped Lua source.**

This is one of the highest-value findings in the client because the game's own UI already consumes structured nearby-player and target objects. Future tooling should reuse these data paths before falling back to broad memory scans.

## 1. Nearby peaceful players

Source: `MainUI_NearByPlayers_PlayersTab.lua`.

The UI runs a coroutine every 5 seconds and calls:

`Game.GetNearByPeacePlayers(MaxPlayers)`

with `MaxPlayers = 6` in the stock UI.

For every returned `playerData`, the shipped Lua directly reads:

- `playerData.Name`
- `playerData.Level`
- `playerData.FactionID`
- `playerData.MaxHP`
- `playerData.HP`
- `playerData.GuildName`
- `playerData.AvartaID`
- `playerData.TeamRank`
- `playerData.RoleID`

It converts `FactionID` through `Game.GetFactionName(...)` and uses `RoleID` for `Game.SelectTarget(RoleID)`.

### Consequence

The client already exposes the exact data needed for a nearby-player table such as:

`Name | RoleID | Level | Faction | HP | MaxHP | HP% | Guild | TeamRank`

without OCR and without requiring party membership.

This directly supports the desired scanner/filter model for buffing friendly nearby players.

## 2. Nearby enemies

Source: `MainUI_NearByPlayers_EnemiesTab.lua`.

The equivalent hostile-player UI calls:

`Game.GetNearByEnemies(false, true, MaxPlayers)`

and consumes the same visible schema:

- Name
- Level
- FactionID
- MaxHP
- HP
- GuildName
- AvartaID
- TeamRank
- RoleID.

Again, the selected entry is targeted by `Game.SelectTarget(RoleID)`.

## 3. Current selected target object

Source: `MainUI_OtherHeader.lua`.

The UI obtains:

`target = Game.SelectedTarget`

and directly uses these target fields:

- `RoleID`
- `Type`
- `Avarta`
- `Name`
- `HPPercent`
- `MPPercent`
- `RagePercent`
- `EnergyPercent`
- `Level`
- `FactionID`
- `MonsterBelongState` for monster/boss ownership coloring.

It also calls:

`Game.GetTargetBuffIcons(target.RoleID)`

and renders up to 10 returned buff icons.

### Object-type-aware UI behavior

For `C_DynamicObjectType.Role` the UI displays:

- HP%;
- MP%;
- Rage%;
- faction;
- level;
- target buffs.

For `Spirit` it uses `EnergyPercent` instead.

For Monster/Boss/Pet it uses HP, type and level semantics. Boss HP is visually split into three bars but derives from the same `HPPercent`.

### Consequence

`Game.SelectedTarget` is a semantic state object, not merely a native pointer to a visual target frame. It is a strong source for target validation after `Game.SelectTarget`.

## 4. Local player state

Source: `MainUI_RoleHeader.lua` and Auto engine Lua.

The UI directly reads from `Game.RoleData`:

- `Name`
- `Level`
- `AvartaID`
- `HP`
- `MaxHP`
- `MP`
- `MaxMP`
- `Rage`
- `MaxRage`

Other auto source directly uses:

- `HPPercent`
- `MPPercent`
- `FactionID`
- `TeamID`
- `MapID`
- `Position.X/Y`
- `IsDeath`
- `IsRiding`
- `AutoSettings`.

This is the correct semantic local-player context for state machines.

## 5. Nearby NPC and ground item pack

Source: `MainUI_BackgroundWork.lua`.

Every ~1 second the stock UI calls:

- `Game.GetNearestNPC()`
- `Game.GetNearestItemPack()`.

For the nearest NPC it consumes:

- `nearestNPCData.Position`
- `nearestNPCData.Name`
- `nearestNPCData.RoleID`.

If distance <= 100, it exposes a talk button whose `Tag` is the NPC RoleID.

For the nearest item pack it consumes:

- `nearestItemPackData.Position`
- `nearestItemPackData.RoleID`.

If distance <= 100, the pickup button's `Tag` stores the item-pack RoleID.

## 6. Nearby enemy-ID scanner already runs in stock MainUI

`MainUI_BackgroundWork` calls:

`Game.GetNearbyEnemyIDs(true, false)`

every ~2 seconds and keeps an `Enemies` list. `SelectNextEnemy()` cycles IDs and uses `Game.SelectTarget(targetID)`.

This is another proof that structured world scanning is a normal client operation, not a special memory-hacking concept.

## 7. Direct consequence for the external Entity Scanner

A good normalized runtime model can be built around the game APIs:

```text
LocalPlayer
  <- Game.RoleData

NearbyPeacePlayers
  <- Game.GetNearByPeacePlayers(limit)

NearbyEnemies
  <- Game.GetNearByEnemies(...)

CurrentTarget
  <- Game.SelectedTarget

NearestNPC
  <- Game.GetNearestNPC(...)

Nearby/NearestLoot
  <- Game.GetNearbyItemPack / GetNearestItemPack
```

Then copy the needed fields into the tool's own read-only snapshots. Do not hold client object pointers longer than needed.

## 8. Auto Buff relevance

For each peaceful-player record, the stock UI already proves availability of:

- RoleID;
- HP;
- MaxHP;
- Faction;
- Name;
- Guild;
- team rank.

Therefore policies such as:

- filter by name / RoleID / faction / guild;
- compute HP%;
- sort by MaxHP descending;
- select a low-HP friendly target by RoleID

can be performed from structured client data.

The **action** still needs to run through the valid Game/Lua action path on Unity/main thread; this document only establishes the read/query schema.

## 9. AOI limitation remains

These APIs expose entities the client currently knows about. They do not imply visibility of every player on the entire map/server. Server area-of-interest replication remains the practical boundary.

## 10. What future AI should not repeat

Do not restart from Cheat Engine by scanning an arbitrary HP value merely to learn Name/RoleID/HP/MaxHP/Faction/Guild for nearby players. The shipped UI source already documents the structured query route and field names above.
