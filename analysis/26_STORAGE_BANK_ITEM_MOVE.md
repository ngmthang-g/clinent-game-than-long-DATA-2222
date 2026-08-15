# Storage / bank / item move semantics

Status: **VERIFIED from decrypted `Storage.lua`, `Global_Constants.lua`, bag-grid/event code and packet constants.**

This subsystem is useful because it proves the client can move a specific live item instance between logical item sites with one semantic request. A future inventory controller can therefore support “cất đồ vào kho” as an alternative to selling.

## Item-site constants

Relevant `C_ItemSite` values:

- Bag = `10`
- Storage = `11`
- Storage_2 = `12`
- Storage_3 = `13`
- Storage_4 = `14`
- Storage_5 = `15`.

Other sites are documented in `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

## Exact move-item action

`C_ItemAction.Move = 5`.

Packet:

`CMD_ITEM_ACTION = 100005`.

### Bag -> Storage

`Storage:RequestAddItemToStorage(dbItemData)` sends:

`5:itemInstanceID:storageSite`

where:

- `5` = `C_ItemAction.Move`
- `itemInstanceID` = `dbItemData.ID`
- `storageSite` = 11..15 for the current storage tab.

### Storage -> Bag

`Storage:RequestTakeOutItemFromStorage(dbItemData)` sends:

`5:itemInstanceID:10`.

Again, the request uses the **live item instance ID**, not template `ItemID` and not screen slot coordinates.

## Client-side guards

Before putting an item into storage, the shipped UI checks:

- current `dbItemData.Site == C_ItemSite.Bag`;
- quest-item range `40000000 <= ItemID < 50000000` is rejected.

Before taking an item out, it verifies the item currently belongs to Storage/Storage_2..5.

These guards should be preserved in any automation unless stronger server/data rules are known.

## Storage sorting

Storage sort sends the same bag-sort packet used by the normal bag:

`CMD_BAG_SORT = 100006`

payload:

`storageSite`

So sorting a storage page is a semantic request, not a need to click a visible “Sắp xếp” button.

## Bank money actions

Packet:

`CMD_ROLE_FEATURE_ACTION = 200061`.

`C_RoleFeaturesAction` values:

- AddMoneyToStorage = `20`
- WithdrawMoneyFromStorage = `21`.

Exact payloads:

- deposit: `20:amount`
- withdraw: `21:amount`.

The UI constrains amount using current `Game.RoleData.Money` or `Game.RoleData.BankMoney`.

## Item update/state proof

Storage and Bag grids participate in the same structured item-event system described in `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

After a move request, use semantic proof such as:

- RemoveItem/update from source site;
- AddItem/update at destination site;
- UpdateItemsList followed by fresh `Game.GetItemsAtSite(site)`;
- current item `Site` changed as expected.

Never assume a move succeeded because a fixed delay elapsed.

## Automation use case

A safe “Auto Store” inner loop can be:

```text
WAIT valid Storage service/UI state
 -> scan current Bag instances
 -> filter keep/store policy
 -> choose ONE current instance
 -> send 100005 `5:instanceID:storageSite`
 -> wait item-site event/state proof
 -> rescan
 -> repeat
```

This is structurally identical to mutation-safe Auto Sell: one current item -> one mutable action -> server/event proof -> fresh scan.

## What is not yet claimed

This document does **not** claim a universal way to open storage from any map/NPC. `CMD_OPEN_STORAGE = 200052` exists, but the exact service/dialog path to the desired warehouse NPC should be taken from actual GameDialog/NPC context rather than invented.

## Future AI rule

Do not implement storage by dragging item icons with the mouse if the internal item move action is available. Keep the identity distinction:

`ID = live instance`, `ItemID = template`, `Position = slot`, `Site = logical container`.
