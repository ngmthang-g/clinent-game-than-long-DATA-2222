# Bag grid / NPC Shop UI runtime semantics

Status: **VERIFIED from `BagItemsGrid.lua`, `RoleInfo_BagTab.lua`, `NPCShop.lua`, `NPCShop_SellItemTab.lua`, `TCPCmdEventHandler.lua`.**

This is the detailed UI/runtime donor for Auto Sell and inventory management.

## Bag grid is semantic data, not an image grid

`BagItemsGrid` creates 100 display slots (`MaxGridItems = 100`) but fills them from:

`Game.GetItemsAtSite(Site)`.

Every returned `dbItemData` is placed by:

`position = dbItemData.Position`.

The UI does not infer inventory content from sprites. It renders structured DB item records into fixed logical positions.

## Important item instance identity

`BagItemsGrid:RemoveItem(dbID)` resolves:

`oldItem = Game.GetItemData(dbID)`

and compares current item records using:

`dbItemData.ID == dbID`.

This reinforces the three-way distinction:

- `ID` = live item/database instance ID;
- `ItemID` = template/type ID;
- `Position` = logical bag position.

Sell/action packets normally use the live instance `ID`.

## Bag update lifecycle

`TCPCmdEventHandler` routes item events to all registered bag-grid UIs.

### AddItem

Event data includes at least:

`data.Site`.

For Bag site, the event is sent to:

`G_UIGroup.ItemsGrids.Bag:Update(eventType, data)`.

`BagItemsGrid:ReceiveUpdate(AddItem, value)` then:

- `AddItem(value, true)`;
- invokes optional update callback.

### RemoveItem

The inbound string is parsed as:

`site:dbID:position`.

For Bag site it routes `dbID` to all bag grids.

`BagItemsGrid` clears the item whose live `ID == dbID` and then refilters.

### UpdateItemsList

All bag/storage grids are asked to update. BagItemsGrid then performs:

`Refresh(true)`

which clears and re-reads `Game.GetItemsAtSite(Site)`.

### Auto Sell consequence

After sending one sell request, a very strong completion proof is:

- `RemoveItem` for the sold instance; and/or
- `UpdateItemsList` followed by a fresh scan; and/or
- shop data/money update consistent with sale.

Then choose the next item from the **new** current state.

## Bag filtering in stock UI

`BagItemsGrid:DoFilter()` classifies by `Game.GetItemType(ItemID)`.

Built-in visible categories include:

- `Equip`
- `ScriptItem` / `CommonItem`
- `Gem`
- `Medicine`.

This confirms item filtering is already intended to be semantic.

## Exact bag site constants

Relevant `C_ItemSite` values:

- Body = 0
- Pet = 1
- Mount = 2
- Pneuma = 3
- WeaponVisual = 4
- Pet reserved = 5/6/7
- **Bag = 10**
- Storage = 11
- Storage_2..5 = 12..15
- NormalGemBag = 16
- UniversalGemBag = 17
- FashionGemBag = 19
- SoulStoneBag = 21
- PneumaBag = 22
- Stall = 100
- Trade = 200.

This is useful when interpreting `Site` fields/events.

## Exact RoleInfo bag actions

`RoleInfo_BagTab` builds semantic actions based on the current item type.

`CMD_ITEM_ACTION = 100005` supports at least:

- Equip = action `1`, payload `1:instanceID`
- Use = action `3`, payload `3:instanceID`
- Abandon = action `4`, payload `4:instanceID`
- Split = action `8`, payload `8:instanceID:quantity`
- EquipPetEquip = `11`
- PutToPetEquipReserved = `19`
- PutPneumaFromBagToPneumaBag = `30`.

The source includes confirmation MessageBoxes for destructive/binding-sensitive actions. Do not bypass those semantics casually in an automation feature.

## Bag sort

`RoleInfo_BagTab:ButtonSortBagClicked()` sends:

`CMD_BAG_SORT = 100006`

payload:

`C_ItemSite.Bag = "10"`.

So bag sorting is a semantic request, not a requirement to open the bag and click a screen button.

## NPC Shop lifecycle

Inbound `CMD_NPC_SHOP_DATA = 200034` opens or refreshes `NPCShop`.

`NPCShop:RefreshData(shopData)` reads at least:

- `shopData.CategoryName`
- `shopData.IsGuildShop`.

If `IsGuildShop == true`, sell tab interaction is disabled.

Otherwise `SellItemTab:SetData(shopData)` is populated.

### Auto Sell guard

Do not attempt selling merely because an NPC was clicked. Wait for current `NPCShop`/shopData and reject a guild shop where the sell tab is disabled.

## Sell-tab runtime data

`NPCShop_SellItemTab` stores `CurrentShopData` and consumes:

- `CurrentShopData.NpcShopID`
- `CurrentShopData.ID` (ShopID)
- `CurrentShopData.TotalSellItem`.

`TotalSellItem` is the shop's recent sold/buy-back list, capped visually to 10 entries.

Each listed sold item uses structured fields such as:

- ID
- ItemID
- Quantity
- Bound.

## Exact sell validation

Before sale, shipped Lua rejects:

1. quest ItemID range `40000000 <= ItemID < 50000000`;
2. any item where `Game.IsItemSellable(ItemID) == false`.

The same checks are used both for normal item action and Quick Sell.

## Quick Sell UI does not use a different packet

`ToggleQuickSell` only changes what a click on a bag item means.

If enabled and item passes validation, it simply calls the same:

`RequestSellItem(dbItemData)`.

Exact request:

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

payload:

`dbItemData.ID:CurrentShopData.NpcShopID:CurrentShopData.ID`.

So “Bán nhanh” is only a UI convenience mode. An internal Auto Sell can skip toggling it and invoke the semantic request for one chosen item instance.

## Buy-back packet also recovered

`ButtonBuyBackItemClicked()` sends:

`CMD_NPC_SHOP_BUY_REQUEST = 200035`

payload:

`itemInstanceID:NpcShopID:ShopID:Quantity:1`.

The final `1` is the buy-back mode used by this path.

This is useful mainly for understanding shop state; Auto Sell should not automatically buy back items.

## Sell price display semantics

For sold item display, the UI uses:

`Game.GetItemBasePrice(ItemID) * Quantity`.

Currency display chooses bound money when:

- `dbItemData.Bound == true`, or
- `Game.IsItemSellToShopWithBoundMoney(ItemID) == true`.

Otherwise it uses normal money display.

## Recommended Auto Sell inner loop

```text
WAIT NPCShop current shopData
 -> SCAN Game.GetItemsAtSite(Bag)
 -> FILTER current item instances
 -> choose ONE current item
 -> SEND 200036 instanceID:NpcShopID:ShopID
 -> WAIT RemoveItem / UpdateItemsList / shop-money state
 -> RESCAN
 -> repeat
```

Never save all 100 slot numbers and sell against that stale slot list.

## Better than the old “sell 90 times” fallback

Because the client provides:

- current bag item list;
- exact instance IDs;
- sellability checks;
- event-driven RemoveItem/UpdateItemsList;

there is no technical need to blindly issue 90 sell clicks when the semantic bridge is functioning. Stop when the current filtered scan has no more sell candidates.
