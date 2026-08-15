# Built-in loot pickup / item-pack filter engine

Status: **VERIFIED from decrypted `AutoFight_Main.lua`, `PickUp.lua` and item/config APIs.**

The frozen client already has a semantic ground-loot engine. Future automation should reuse these concepts instead of detecting dropped-item labels/pixels.

## Ground item-pack discovery

When Auto pickup is enabled, `AutoFight_Main:DoPickItem()` calls:

`Game.GetNearbyItemPack(predicate, centerPosition)`.

The predicate directly consumes item-pack/world-object fields:

- `Type`
- `RoleID`
- `Position`.

It rejects:

- non-`ItemPack` objects;
- packs already processed in `ItemPackListAreadyPick`;
- packs beyond configured `PickRanger`.

## Reachability and movement

Before interaction:

`Game.HasPath(currentPosition, ItemPack.Position)`

is checked.

If unreachable, the pack is marked/skipped.

If distance > 100:

`Game.MoveToEx(ItemPack.Position.X, ItemPack.Position.Y, success, fail)`

and the success callback calls:

`Game.ClickToObject(ItemPack.RoleID)`.

If already near enough, it calls `Game.ClickToObject(RoleID)` directly.

This is a semantic world-object interaction path, not a mouse click on rendered loot.

## Item-pack content lifecycle

After the pack interaction returns its item list, `RevicePackItemData(itemPackID, items)` decides what to pick.

The current pack RoleID is tracked so responses from stale/other packs are rejected.

## Pick-all action

If filtering is disabled and free bag capacity is sufficient, the client calls:

`Game.PickUpItemFromItemPack(itemPackID, -1, 1)`.

`slotIndex = -1` therefore represents the built-in “pick all” path in this donor code.

If capacity is insufficient, built-in Auto pickup is turned off rather than blindly continuing.

## Filter settings schema

`FilterItemSettings` is serialized as five underscore-separated fields:

`material_equipment_minStar_quest_gem`

Specifically:

1. pick material flag;
2. pick equipment flag;
3. minimum equipment star;
4. pick quest item flag;
5. pick gem flag.

The UI builds the same five-value string.

## ID-family logic used by the shipped engine

For each item in a pack:

`Index = floor(ItemID / 10000000)`.

The frozen Auto code uses:

- family `2` or `3` -> material;
- family `4` -> quest item;
- family `5` -> gem.

This is not an external guess; it is the actual filtering heuristic in shipped Lua.

However, future code can prefer semantic template/API classification where available instead of assuming this ID-family scheme is universally valid outside the exact paths where the game itself uses it.

## Equipment/star filtering

For equipment candidates the client reads:

`itemData = Game.GetItemTemplateData(ItemID)`

and requires `itemData.EquipData ~= nil`.

Star selection follows this source logic:

1. start with `itemData.EquipData.Star`;
2. DragonTattoo uses live `dbItemData.Properties[C_ItemProperty.DragonTattooStar]`;
3. otherwise if live `EquipStar` property exists, use `dbItemData.Properties[C_ItemProperty.EquipStar]`;
4. otherwise if template Star >= 10, source forces display/filter star value to 1.

Then the item is picked only when `totalStars >= configuredMinimumStar`.

This matters because crafted/live equipment star can differ from a static template value.

## Single-item pickup

For filtered items, the action is:

`Game.PickUpItemFromItemPack(itemPackID, slotIndex, 1)`.

The source checks free bag space before each pickup and stops Auto pickup when capacity is exhausted.

## Special skip condition

The built-in engine skips Auto pickup while:

`Game.HasBuff(30008009)`

and shows a notification mentioning **Càn Khôn Hồ**.

This exact BuffID/behavior is preserved because it is a real source guard; its deeper gameplay reason should not be generalized beyond the frozen client without additional evidence.

## Auto-use item configuration

`PickUp.lua` also supports timed automatic use of Bag items.

It lists `ScriptItem` and `Medicine` items from:

`Game.GetItemsAtSite(C_ItemSite.Bag)`.

The serialized using-item list stores:

`itemDBID,seconds`

where `itemDBID` is the live `dbItemData.ID` and delay is validated in range 10..86400 seconds. Up to about 20 configured entries are allowed by the UI logic.

Because the list uses live DB instance IDs, a robust derivative implementation should revalidate that the instance still exists before every use rather than treating the stored ID as a permanent template identifier.

## Auto Train integration

The shipped Auto engine composes:

`target combat -> drop appears -> nearby item-pack scan -> path check -> semantic object click -> content response -> capacity/filter decision -> semantic pickup`.

This makes loot a separate stateful subsystem, not a series of blind screen clicks.

## Recommended external snapshot/state machine

```text
SCAN nearby packs
 -> filter range/reachability/already-seen
 -> choose ONE pack
 -> move/interact
 -> WAIT pack contents
 -> choose ONE pickup action or pick-all
 -> WAIT bag/item state update
 -> rescan
```

Do not queue pickups against an old pack/item list after the bag mutates.

## Future AI rule

Do not rebuild ground-loot detection from OCR. The client already exposes nearby ItemPack RoleIDs/positions and exact semantic pickup calls.
