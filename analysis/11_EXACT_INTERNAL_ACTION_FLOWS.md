# Exact internal action flows recovered from Lua

Status: **VERIFIED source-level payload construction**.

## Revive / reincarnation

`C_RevivalType`: Normal=`1`, NewbieRevival=`2`, SkillRevival=`3`.

`Revival` UI:
- Tân thủ → `ButtonNewbieReviveClicked`
- Hồi sinh → `ButtonSkillReviveClicked`
- Đầu thai → `ButtonGoToInfernalClicked`

All send `CMD_REVIVE_DATA = 200063` with one-number payload: normal `"1"`, newbie `"2"`, skill revive `"3"`.

Inbound `TCPCmdHandler` handles the same packet to open/update/close Revival and triggers `AutoFight_Main:DeathActive()` when the frame opens.

## Sell one item to NPC shop

`NPCShop_SellItemTab:RequestSellItem(dbItemData)` constructs:

`dbItemData.ID : CurrentShopData.NpcShopID : CurrentShopData.ID`

and sends `CMD_NPC_SHOP_SELL_REQUEST = 200036`.

Important:
- `dbItemData.ID` = item **instance/database ID**;
- `ItemID` = item template ID;
- original script blocks quest ItemID range `40000000..49999999`;
- original script checks `Game.IsItemSellable(dbItemData.ItemID)`.

This resolves the previously unknown exact sell request.

## Buy back

`CMD_NPC_SHOP_BUY_REQUEST = 200035` payload:

`dbItemData.ID : NpcShopID : ShopID : Quantity : 1`

## Bag sort

`RoleInfo_BagTab:ButtonSortBagClicked()` sends `CMD_BAG_SORT = 100006` with `C_ItemSite.Bag`. Bag=`10`, so exact payload is `"10"`.

## Item actions

`C_ItemAction` includes Equip=1, Unequip=2, Use=3, Abandon=4, Move=5, UnequipMount=6, Merge=7, Split=8, Destroy=9, UnequipWeaponVisual=10, EquipPetEquip=11, UnequipPetEquip=12 plus gem/soul/pneuma actions.

Through `CMD_ITEM_ACTION = 100005`:
- Equip: `1:instanceID`
- Use: `3:instanceID`
- Abandon: `4:instanceID`
- Split: `8:instanceID:quantity`

## Dynamic GameDialog

`GameDialog` receives `Selections[selectionID] = visibleText`. Generated buttons store `selectionID` in their Tag.

On function-button click it sends `CMD_SHOW_GAMEDIALOG = 100007` with:

`selectionID : SelectedItemID`

Default item is `-1` when no award-item selection is required.

Therefore generic NPC functions should be automated by waiting for actual GameDialog data, inspecting `Selections`, choosing semantic text, sending the real selection ID, and waiting for server/UI state change. Do not invent a fixed “Trị liệu” ID.

## NPC shop acknowledgement

Inbound `CMD_NPC_SHOP_DATA = 200034`:
- if `NPCShop` absent → `GUI.CallUI("NPCShop", shopData)`;
- otherwise → refresh existing NPCShop.

This is a good state proof that the shop is actually open.

## MessageBox

`MessageBox` stores `OKCallback` / `CancelCallback`; button handlers destroy the UI then invoke the supplied callback. Prefer this semantic flow instead of stale native UIButton pointers.

## Server-authoritative inventory loop

Safe sell loop:
1. get current item instance;
2. send one sell request;
3. wait for inventory/shop update;
4. rescan bag;
5. choose next instance.

Do not cache a slot list and replay it after mutations.
