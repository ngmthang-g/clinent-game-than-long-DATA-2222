# Feature specification — Auto Sell

Status: **core sell request VERIFIED; NPC dialog choice remains state-dependent**.

## Data

Use `Game.GetFreeBagSpace()`, `Game.GetItemsAtSite(C_ItemSite.Bag)`, instance `ID`, template `ItemID`, `Position`, `Quantity`, `Bound`, plus `GetItemType`, `GetEquipType`, `IsItemSellable`, `IsItemThrowable`.

Prefer direct `GetFreeBagSpace()` instead of opening bag UI and counting cells.

## NPC routing

Use `Game.GetNPCPosition(npcID)`, `Game.GoTo`, `Game.GetNearestNPC` and semantic interaction.

Static DB confirms on Map 5 Lâu Lan:
- Ba Nhĩ = NPC 328
- Mã Kiêu Minh = NPC 373

No static X/Y is asserted from `AutoPath/NPCData`.

## Shop opening

Wait for dynamic `GameDialog`, inspect `Selections`, choose shop/trade semantic option, then wait for `CMD_NPC_SHOP_DATA` / NPCShop state.

## Exact sell request

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload: `itemInstanceID:NpcShopID:ShopID`.

## Filtering

At minimum:
- never confuse ItemID template with instance ID;
- block original quest range `40000000..49999999`;
- require `IsItemSellable(ItemID)`;
- honor whitelist.

Keep weapon condition: `GetItemType(ItemID)==Equip AND GetEquipType(ItemID)==Weapon`.

## Mutation-safe loop

`SCAN -> choose ONE item -> send ONE sell -> wait server inventory/shop update -> RESCAN -> repeat`.

Do not pre-cache 90 slot clicks.

After selling, return to saved train map/position, verify state, then resume Train.
