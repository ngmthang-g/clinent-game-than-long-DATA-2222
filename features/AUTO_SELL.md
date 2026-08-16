# Feature specification — Auto Sell

Status: **core sell request + inventory/shop lifecycle VERIFIED; per-NPC service confirmation remains runtime-dependent**.

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

Current Lâu Lan Auto Sell knowledge is separated by evidence level in `database/AUTO_SELL_VENDOR_MAP.md`.

Static DB confirms Map 5 Lâu Lan identities:

- Ba Nhĩ = NPC 328;
- Mã Kiêu Minh = NPC 373;
- Hiệp Hàng = NPC 341, merchant-archetype `ResName=npcXiYuTuoDuiShangRen`;
- Chu Thập Tam = NPC 398, blacksmith-archetype `ResName=TieJiang`.

The user has identified Ba Nhĩ and Mã Kiêu Minh as selling destinations in gameplay; keep that as **USER-REPORTED SERVICE** until the exact runtime GameDialog/NPCShop path is captured. Do not mislabel it as static Config proof.

No static/manual X/Y is canonical. Query `Game.GetNPCPosition(npcID)` at action time.

## Vendor verification rule

A candidate becomes a **runtime-verified normal sell vendor** only when the actual interaction path proves:

```text
candidate NPC interaction
 -> optional current GameDialog selection
 -> inbound CMD_NPC_SHOP_DATA = 200034
 -> current NPCShop data present
 -> IsGuildShop == false
 -> current NpcShopID + ShopID captured
```

Opening some unrelated UI or dialog is not enough.

If one disposable item is used for verification, success proof is the normal sell lifecycle: `RemoveItem` / `UpdateItemsList` / consistent shop-money state.

## Shop opening/readiness

If the NPC uses a dialog menu:

1. wait for active `GameDialog`;
2. inspect current `Selections`;
3. choose the actual shop/trade selection ID by current visible text;
4. wait for inbound `CMD_NPC_SHOP_DATA = 200034`;
5. require current `NPCShop`/shopData before selling.

`NPCShop:RefreshData(shopData)` exposes `shopData.IsGuildShop`; guild shops disable the sell tab and are not a valid normal sell destination.

Do not persist one observed dialog selection ID as a permanent global constant unless repeatable evidence proves it stable.

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

Canonical compact keep/sell rules: `database/AUTO_SELL_CLASSIFICATION.md`.

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

Optionally stop earlier when the configured free-space target has been reached.

The old fallback “bấm bán 90 lần” is unnecessary once the semantic sell path is operational.

## Weapon/item keep filtering

Use `database/AUTO_SELL_CLASSIFICATION.md`, runtime semantic item/equipment classification and only the static fields needed by the actual policy. Do not classify by icon/OCR.

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
- do not upgrade a vendor candidate to runtime-verified from name/ResName alone.

Deep donor detail: `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.
