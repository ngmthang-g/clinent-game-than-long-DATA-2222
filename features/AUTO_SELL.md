# Feature specification — Auto Sell

Status: **core sell request + inventory/shop lifecycle VERIFIED; NPC dialog choice remains state-dependent**.

## Data

Use semantic inventory APIs:

- `Game.GetFreeBagSpace()`
- `Game.GetItemsAtSite(C_ItemSite.Bag)`
- live item `ID`
- template `ItemID`
- `Position`
- `Quantity`
- `Bound`
- `GetItemType`
- `GetEquipType`
- `IsItemSellable`
- `IsItemThrowable`.

Prefer direct `GetFreeBagSpace()` instead of opening the bag UI and counting cells.

`BagItemsGrid` itself is a 100-slot UI populated from `Game.GetItemsAtSite(Bag)`, so visual cell scanning is unnecessary.

## NPC routing

Use `GoToNPC(mapID,npcID)` or its semantic steps:

`Game.GetNPCPosition -> Game.GoTo -> Game.ClickNPC`.

Static DB confirms on Map 5 Lâu Lan:

- Ba Nhĩ = NPC 328
- Mã Kiêu Minh = NPC 373.

No static X/Y is asserted from `AutoPath/NPCData`.

## Shop opening/readiness

If the NPC uses a dialog menu:

1. wait for active `GameDialog`;
2. inspect current `Selections`;
3. choose the actual shop/trade selection ID;
4. wait for inbound `CMD_NPC_SHOP_DATA = 200034`;
5. require current `NPCShop`/shopData before selling.

`NPCShop:RefreshData(shopData)` exposes `shopData.IsGuildShop`; guild shops disable the sell tab and are not a valid normal sell destination.

## Exact sell request

Packet:

`CMD_NPC_SHOP_SELL_REQUEST = 200036`.

Payload:

`itemInstanceID:NpcShopID:ShopID`.

The first value is `dbItemData.ID` — the live item instance/database ID — not template ItemID and not Position.

`NpcShopID` and `ShopID` come from the **current** `NPCShop` data:

- `CurrentShopData.NpcShopID`
- `CurrentShopData.ID`.

Do not invent/hardcode them when current shop state is available.

## Quick Sell semantics

The shipped `ToggleQuickSell` only changes the click behavior of the bag grid. After validation it calls the same `RequestSellItem(dbItemData)` and sends the same packet above.

Therefore an internal Auto Sell does not need to toggle Quick Sell or click the screen cells.

## Original client validation

Before selling, stock Lua blocks:

- quest ItemID range `40000000 <= ItemID < 50000000`;
- items where `Game.IsItemSellable(ItemID) == false`.

Preserve these guards and add the user's keep/sell whitelist.

## Mutation-safe confirmation

Inbound `RemoveItem` data is parsed as:

`site:dbID:position`.

For Bag site, bag UIs remove the live item whose `ID == dbID`.

`UpdateItemsList` forces bag grids to refresh from `Game.GetItemsAtSite(Bag)`.

So the correct inner loop is:

```text
SCAN current bag
 -> choose ONE current instance
 -> send ONE sell
 -> WAIT RemoveItem(instanceID) / UpdateItemsList / consistent shop state
 -> RESCAN
 -> choose next
```

Do not cache a list of 90 slot clicks.

## Stop condition

When a fresh filtered bag scan contains zero sell candidates, selling is complete.

The old fallback “bấm bán 90 lần” is unnecessary once the semantic sell path is operational.

## Weapon/item keep filtering

Use the semantic item/equipment classification documented in `analysis/04_INVENTORY_ITEMS_SHOP.md` and the frozen Config database. Do not classify by icon/OCR.

Always keep `ID` (instance), `ItemID` (template) and `Position` (slot) distinct.

## Return to Auto Train

Before selling:

- save prior Auto mode;
- save train map/position;
- stop Train semantically.

After selling:

1. leave/close shop as appropriate;
2. `Game.GoTo(savedMap,savedX,savedY)`;
3. verify alive + map + loading + position state;
4. resume `AutoFight_Main:StartAutoFight(C_AutoModel.Train)`.

## Safety

- Captcha active -> pause and require user interaction.
- dead/Revival -> hand over to revive state machine.
- no current shop data -> do not send sell.
- one mutable item action at a time.
- never call client response handlers to fake removal/sale.

Deep donor detail: `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.
