# Inventory / Items / Shop / Auto Sell

## 1. Kết luận lớn

Đây là một trong các subsystem được metadata mô tả rõ nhất. Client có API semantic đủ để:

- biết số ô trống;
- enumerate item;
- phân biệt item instance và item template;
- phân loại Equip/Common/Gem/Medicine/PetEquip;
- phân loại loại trang bị, gồm Weapon;
- biết sellable/throwable;
- lấy base/buy price, stack, bound, quantity/durability;
- quan sát server response khi item/money/shop state thay đổi.

Vì vậy inventory scanner không nên dựa vào OCR, pixel, icon hay kéo tay nải xuống để đếm ô.

## 2. API đã thấy

### Bag/list/query

- `GetFreeBagSpace()`
- `GetTotalItems`
- `GetItems`
- `GetItemsAtSite(site)`
- `GetItemAtSite(site, pos)`
- `FindItems`
- `FindItem`
- `CountItem`

### Item data/template

- `GetItemData(dbID)`
- `GetItemTemplateData`
- `GetItemType(itemID)`
- `GetEquipType(itemID)`
- `GetPetEquipType(itemID)`
- `GetItemName`
- `GetItemIcon`
- `GetItemBasePrice`
- `GetItemBuyPrice`
- `GetItemMaxStack`
- `GetItemExtraHint`

### Rules

- `IsItemThrowable(itemID)`
- `IsItemSellable(itemID)`
- `IsItemSellToShopWithBoundMoney(itemID)`
- `GetEquipBoundRule`
- `CanEquipIdentified`

### Equipment/gem details

- `GetEquipVisualID`
- `GetEquipStar`
- `GetEquipLevel`
- `GetEquipEnhanceData`
- `GetEquipIdentifyValue`
- `GetEquipSet`
- `GetGemType`
- `GetGemLevel`
- `IsUniversalGem`
- HeroicOrder/Signet/PetEquip-related methods also exist.

## 3. LuaItemData — ba ID không được nhầm

Metadata/analysis trước đó cho thấy item instance có các property/field names:

- `ID`
- `ItemID`
- `Site`
- `Position`
- `Bound`
- `Quantity`
- `Durability`
- và các thông tin khác.

### Ý nghĩa

- `ID`: ID của **instance cụ thể** đang tồn tại.
- `ItemID`: ID **template/resource** của loại item.
- `Position`: slot/position trong container.

Một lỗi rất nguy hiểm là dùng `ItemID` như instance ID hoặc tin `Position` sẽ không đổi sau khi server update bag.

## 4. ItemType đã thấy

Enum/string evidence gồm ít nhất:

- `Equip`
- `CommonItem`
- `Gem`
- `Medicine`
- `PetEquip`

Exact numeric enum values chưa được ghi ở KB này; hãy resolve enum metadata nếu cần code cứng giá trị.

## 5. EquipType đã thấy

Các category đã ghi nhận:

- `Weapon`
- `Hat`
- `Cloth`
- `Gloves`
- `Shoes`
- `Belt`
- `Ring`
- `Necklace`
- `Mount`
- `Ring_2`
- `Amulet`
- `Amulet_2`
- `Cuff`
- `Shoulderpads`
- `Fashion`
- `Dart`
- `Soul`
- `DragonTattoo`
- `HeroicOrder`
- `Signet`
- `WeaponVisual`
- có thể còn category khác.

### Nhận biết vũ khí

Logic semantic:

```text
GetItemType(ItemID) == Equip
AND
GetEquipType(ItemID) == Weapon
=> item là vũ khí
```

Không cần OCR/icon/name matching.

## 6. Filter an toàn

Giả định `không phải Weapon = rác` là sai và nguy hiểm. Nó có thể gồm:

- gem;
- medicine;
- quest item;
- material;
- rare item;
- pet equipment;
- bound/non-sellable item;
- currency-like objects.

### Rule an toàn cho auto sell

Ví dụ:

```text
if Weapon:
    KEEP
else if !IsItemSellable(ItemID):
    KEEP / SKIP
else if whitelist matches:
    KEEP
else:
    SELL_CANDIDATE
```

Có thể thêm filter:

- ItemType
- EquipType
- Bound
- Quantity
- SellPrice/base price
- star/level/quality nếu map được
- protected item IDs.

### Rule an toàn cho auto discard

Chỉ đưa item vào discard candidate khi **cả policy của user và `IsItemThrowable`** cho phép. Không dùng “không phải vũ khí” làm điều kiện đủ.

## 7. Bag-full detection

`GetFreeBagSpace()` là entry point ưu tiên.

Thay vì:

```text
Open bag -> Sort -> Scroll -> Count empty slots visually
```

hãy dùng:

```text
free = GetFreeBagSpace()
if free == 0:
    start sell state machine
```

Có thể vẫn mở bag UI cho mục đích hiển thị/debug, nhưng không nên coi UI là source of truth cho free slots.

## 8. Server-authoritative shop update

Đã thấy các processing/update names:

- `ProcessRemoveItem`
- `ProcessUpdateItemsList`
- `ProcessUpdateMoney`
- `ProcessUpdateTraderState`

và command/event names tương ứng như:

- `CMD_REMOVE_ITEM`
- `CMD_UPDATE_ITEMS_LIST`
- `CMD_UPDATE_MONEY`
- `CMD_UPDATE_TRADER_STATE`.

### Điều này chứng minh gì

Bán item là flow có server confirmation/state sync. Các `Process*` là dấu hiệu inbound/update, **không phải request bán**.

Không gọi `ProcessRemoveItem` để “giả bán”. Làm vậy chỉ có thể sửa state client tạm thời rồi server sync lại hoặc tạo desync.

## 9. Vì sao bán nhiều item phải rescan

Sai:

```text
scan slots 1..100
save list positions
sell pos 1
sell pos 2
sell pos 3
```

Sau mỗi server update, list/slot/position có thể thay đổi.

Đúng hơn:

```text
SCAN current bag
 -> choose ONE candidate by instance ID/current position
 -> send real sell action
 -> WAIT RemoveItem/UpdateItemsList/UpdateMoney or bag change
 -> SCAN AGAIN
 -> choose next
```

Có thể giữ stable instance ID nếu game đảm bảo ID tồn tại đến khi remove, nhưng không được tin tuyệt đối slot snapshot cũ.

## 10. Shop request còn thiếu gì

C# metadata không lộ một helper rõ ràng tên `SellItem()` hoặc `QuickSell()` trong các phát hiện hiện tại. Bằng chứng kiến trúc cho thấy phần shop action có khả năng nằm trong Lua UI và gọi `LuaSystemAPI_Network.SendPacket`.

Vì thế muốn map request bán chính xác, targeted trace tốt nhất là:

1. `ClickNPC(vendorNpcId)`;
2. trace `MainCallUI/CallUI` khi mở shop;
3. trace Lua callback khi chọn sell mode;
4. trace `SendPacket(packetID, payload)` khi tự tay bán **một item**;
5. observe `ProcessRemoveItem` / `ProcessUpdateMoney` / `ProcessUpdateItemsList`.

Sau một trace đúng, document packet/callback và replay bằng state machine.

## 11. State machine đề xuất cho Auto Sell

```text
TRAINING
 -> periodic GetFreeBagSpace
 -> if free > threshold: stay training
 -> if full: suspend combat
 -> choose vendor for current map
 -> move to vendor
 -> ClickNPC
 -> WAIT NPC UI
 -> open trade/shop action
 -> WAIT shop UI / trader state
 -> enter sell mode
 -> SCAN BAG
 -> choose 1 SELL_CANDIDATE
 -> SEND REAL SELL ACTION
 -> WAIT SERVER CONFIRM
 -> SCAN BAG AGAIN
 -> no candidates? close shop
 -> return train position
 -> verify position/map
 -> resume combat
```

Không nên “bấm bán 90 lần” nếu bag list đã đọc được realtime. Fixed 90-click chỉ nên là fallback tạm thời cho prototype.

## 12. Database item offline

`Config.unity3d` có khả năng rất cao chứa static item configuration. Nếu extract được, nên tạo database tĩnh:

```text
ItemID
Name
ItemType
EquipType
BasePrice
MaxStack
Bound/Sell/Throw rules
rarity/quality nếu có
icon/resource refs
```

Runtime scanner sau đó chỉ cần giữ instance fields (`ID`, `ItemID`, position, qty, bound/durability) và join vào database tĩnh.

## 13. Các điểm đã chắc / chưa chắc

### Chắc cao

- API query bag/item tồn tại.
- Weapon có thể phân loại bằng data game.
- sell/update có server-side confirmation semantics.
- slot snapshot có thể stale sau mutation; rescan/state observation là kiến trúc đúng.

### Chưa xác nhận exact

- packetID/payload bán một item;
- Lua callback/menu name cho shop hiện tại;
- numeric enum values của tất cả ItemType/EquipType;
- exact static config table trong `Config.unity3d`.
