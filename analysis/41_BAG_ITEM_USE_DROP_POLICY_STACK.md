# 41 — Bag / use / abandon / destroy / move policy stack

Status: **VERIFIED from shipped bag, DestroyItems, PickUp, AutoFight configuration Lua plus Config `Items/Equips/Medicines/Gems`.** Two shipped Auto settings are explicitly marked incomplete/buggy.

## 1. Item identity rule

Always preserve:

`dbItemData.ID = live instance` != `ItemID = template` != `Position = current slot` != `Site = container`.

Static Config classifies a template. Mutable actions must use a fresh live instance.

## 2. Exact item sites relevant to tool

`C_ItemSite`: Body0, Pet1, Mount2, Pneuma3, WeaponVisual4, PetReserved5..7, Bag10, Storage11..15, NormalGemBag16, UniversalGemBag17, FashionGemBag19, WeaponVisualGemBag20, SoulStoneBag21, PneumaBag22, Stall100, Trade200.

## 3. Exact item actions

`CMD_ITEM_ACTION = 100005`.

`C_ItemAction` frozen values:

- Undefined0
- Equip1
- Unequip2
- Use3
- Abandon4
- Move5
- UnequipMount6
- Merge7
- Split8
- Destroy9
- UnequipWeaponVisual10
- EquipPetEquip11
- UnequipPetEquip12
- PutToGemBag13
- TakeOutFromGemBag14
- PutToSoulStoneBag15
- TakeOutFromSoulStoneBag16
- UnequipPetEquipReserved17
- TogglePetEquipSet18
- PutToPetEquipReserved19
- PutPneumaFromBagToPneumaBag30
- TakeOutPneumaFromPneumaBag31
- EquipPneuma32
- UnequipPneuma33.

Verified common payloads:

- Use: `3:instanceID`
- Abandon: `4:instanceID`
- Move: `5:instanceID:destinationSite`
- Split: `8:instanceID:quantity`
- Destroy batch: `9:id1;id2;id3;...`.

Destroy and Abandon are different destructive operations.

## 4. UI guards

Bag UI offers Use for ScriptItem/Medicine flows. Abandon is guarded by `Game.IsItemThrowable(ItemID)` and asks confirmation. `DestroyItems` can collect up to 35 marked live item instances and warns that destruction cannot be recovered.

Tool must add stricter allowlist/denylist policy before destructive actions; never destroy merely because the client UI allows it.

Bag sort: `CMD_BAG_SORT = 100006`, payload `10` (Bag).

## 5. Static keep/sell/use evidence

`Items.xml`: 5,238 templates. Verified snapshot counts: Sellable=true 4,970; false 268. Throwable=true 5,005; false 233.

`database/static/items/ITEM_POLICY_EXCEPTIONS.csv` materializes templates that are non-sellable, non-throwable or otherwise policy-exception candidates; `ITEM_TYPE_COUNTS.csv` summarizes client TypeDesc families.

Equipment static truth: `Equips.EquipPoint == 0` means Weapon; 4,685 frozen equip templates occupy Weapon. Do not use `Type < 10` as universal weapon test.

Runtime `Game.IsItemSellable`, `Game.IsItemThrowable`, `GetItemType`, `GetEquipType` remains the action-time authority.

## 6. Ground loot

Shipped semantic path:

`GetNearbyItemPack -> HasPath -> MoveToEx -> ClickToObject -> PickUpItemFromItemPack`.

Observed pick-all: `PickUpItemFromItemPack(itemPackID,-1,1)`.

The shipped pickup filter also uses ItemID 10M families and equip star threshold. This is a client heuristic, not a universal semantic taxonomy; retain runtime/template joins for richer keep/sell policy.

## 7. Important incomplete AutoUsingItem / AutoDrop behavior

The UI/config exposes:

- `AutoUsingItem`
- `UsingItemList` entries containing an item DB ID plus interval seconds;
- `IsAutoDropItem`
- `DropItemSettings`.

But no executor consuming AutoUsingItem/UsingItemList or IsAutoDropItem/DropItemSettings was found in the shipped Lua analyzed here.

There is also a concrete load bug in `AutoFight_Main`:

save writes `... IsAutoDropItem | DropItemSettings`, but load assigns both `IsAutoDropItem` and `DropItemSettings` from `PickItemPrams[8]` instead of reading the saved ninth field for DropItemSettings.

Therefore classify:

- manual Use/Abandon/Destroy/Move/Split: VERIFIED;
- AutoUsingItem configuration: CONFIG/UI PRESENT, executor not verified;
- AutoDrop configuration: CONFIG/UI PRESENT + load bug, executor not verified.

Do not tell future tool code that these two shipped auto features are already reliable.
