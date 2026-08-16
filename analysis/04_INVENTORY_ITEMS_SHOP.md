# Inventory / Items / Shop / Auto Sell — current solved model

> Inventory/shop is now one of the best-understood subsystems in the frozen client. Old statements that the sell packet or Config table are unknown are obsolete.

---

## 1. Core conclusion

The client exposes enough semantic runtime/static data to avoid OCR, icon recognition, bag scrolling and blind repeated clicks.

A robust inventory system can:

- read free bag slots;
- enumerate live item instances;
- distinguish live instance ID from template ID and slot/site;
- classify item/equipment type;
- preserve weapons or other protected categories by game data;
- check sellable/throwable rules;
- join live instances to static `Items` / `Equips` / `Medicines` / `Gems` data;
- issue one exact semantic mutation;
- wait for server-authoritative item/money/shop state before continuing.

---

## 2. Runtime query APIs

### Bag / collection

- `GetFreeBagSpace()`
- `GetTotalItems`
- `GetItems`
- `GetItemsAtSite(site)`
- `GetItemAtSite(site,pos)`
- `FindItems`
- `FindItem`
- `CountItem`.

### Item/template

- `GetItemData(dbID)`
- `GetItemTemplateData(ItemID)`
- `GetItemType(ItemID)`
- `GetEquipType(ItemID)`
- `GetPetEquipType(ItemID)`
- `GetItemName`
- `GetItemIcon`
- `GetItemBasePrice`
- `GetItemBuyPrice`
- `GetItemMaxStack`
- `GetItemExtraHint`.

### Rule helpers

- `IsItemThrowable(ItemID)`
- `IsItemSellable(ItemID)`
- `IsItemSellToShopWithBoundMoney(ItemID)`
- equip/bound/identify helpers.

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
- PetEquip/HeroicOrder/Signet-related helpers.

---

## 3. Live item identity — never conflate these fields

Observed `LuaItemData` fields include:

- `ID`
- `ItemID`
- `Site`
- `Position`
- `Bound`
- `Quantity`
- `Durability`.

Meaning:

- `ID` = **live item/database instance ID**;
- `ItemID` = static template/resource ID;
- `Site` = logical container;
- `Position` = current slot inside that container.

Canonical rule:

```text
ID != ItemID != Position != Site
```

Mutation requests such as shop sell/storage move use the **current live instance ID**.

After a mutation, slot/site/list state may change; never keep using an old bag-slot snapshot without a fresh read.

---

## 4. Item/equipment classification

Runtime semantic type names include:

- Equip
- CommonItem
- Gem
- Medicine
- PetEquip.

Equipment categories include Weapon, Hat, Cloth, Gloves, Shoes, Belt, Ring, Necklace, Mount, Amulet, Cuff, Shoulderpads, Fashion, Dart, Soul, DragonTattoo, HeroicOrder, Signet, WeaponVisual and variants.

### Static `Equips.xml` distinction — VERIFIED

`Equips.xml` has both:

- `Type` = specific equipment form/subtype;
- `EquipPoint` = equipment slot/position semantic.

Exact important slot rule:

`EquipPoint == 0` = **Weapon**.

There are **4,685** Equip rows at Weapon position in this snapshot.

Do not classify a weapon only with `Type < 10`; other weapon forms such as Blade/Sickle/Zither exist outside that range.

### Runtime preferred check

When live APIs are available:

```text
GetItemType(ItemID) == Equip
AND
GetEquipType(ItemID) == Weapon
```

Static `EquipPoint==0` is ideal for offline/template policy.

---

## 5. Static item/equipment databases — VERIFIED

`Config.unity3d` extraction proves the exact tables exist.

### `Items.xml`

**5,238 rows**.

Normalized fields already documented include:

`ID, Name, Icon, ItemLevel, RequireLevel, BoundMoney, BasePrice, SellPrice, Throwable, Sellable, Bound, Stack, MaxUsageTimes, DurationHour, ScriptID, TypeDesc, ...`

Snapshot statistics:

- Sellable=true: **4,970**
- Sellable=false: **268**
- Throwable=true: **5,005**
- Throwable=false: **233**.

### `Equips.xml`

**22,763 rows**.

Contains template identity, Type, EquipPoint, level/faction, price, durability, identification, star, BuffID, SetID, visual and base attributes.

### `Medicines.xml`

**692 rows** with medicine price/level/stack/sellability semantics.

### `Gems.xml`

**1,154 rows**.

Canonical schema/detail:

- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

### Static vs live rule

Static rows decide **what the template is**.

Live runtime decides:

- whether the current instance exists;
- where it currently is;
- whether current semantic/server rules allow mutation;
- whether a request succeeded.

---

## 6. Safe keep/sell policy

The rule “not Weapon = trash” is unsafe.

Non-weapon items can include:

- valuable armor/accessories;
- gems;
- medicines;
- quest items;
- materials;
- pet gear;
- rare/bound/non-sellable objects.

A conservative policy can be:

```text
if protected ItemID / whitelist:
    KEEP
else if live/template class is Weapon and policy says keep weapons:
    KEEP
else if !Game.IsItemSellable(ItemID):
    KEEP_OR_SKIP
else if quality/star/level/set/value rules say keep:
    KEEP
else:
    SELL_CANDIDATE
```

Discard policy must additionally require `IsItemThrowable(ItemID)` and explicit user policy.

---

## 7. Bag-full detection — VERIFIED semantic path

Use:

`Game.GetFreeBagSpace()`.

No need for:

```text
open bag -> sort -> scroll -> visually count blank cells
```

Recommended trigger:

```text
free = GetFreeBagSpace()
if free <= configuredThreshold:
    enter BAG_EVALUATION / SELLING policy
```

The visible 100-slot Bag grid is presentation; `Game.GetItemsAtSite(C_ItemSite.Bag)` is the structured content source.

`C_ItemSite.Bag = 10`.

---

## 8. Exact shop sell request — VERIFIED

This is no longer a missing trace.

From decrypted `NPCShop_SellItemTab` Lua:

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload:

```text
itemInstanceID:NpcShopID:ShopID
```

Where:

- `itemInstanceID` = `dbItemData.ID` of the **current live instance**;
- `NpcShopID` = current NPC shop context;
- `ShopID` = `CurrentShopData.ID`.

Original Lua also checks:

- quest-item ID family/range guard;
- `Game.IsItemSellable(ItemID)`.

### Quick Sell

Quick Sell is a UI convenience; it ultimately calls the **same semantic sell request**, not a special bulk-sell protocol.

Canonical detailed evidence:

- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`.

---

## 9. Shop state / server proof

Relevant server/update lifecycle includes:

- `CMD_NPC_SHOP_DATA = 200034` -> shop data/UI state;
- `CMD_REMOVE_ITEM`
- `CMD_UPDATE_ITEMS_LIST`
- `CMD_UPDATE_MONEY`
- `CMD_UPDATE_TRADER_STATE`;
- processors such as `ProcessRemoveItem`, `ProcessUpdateItemsList`, `ProcessUpdateMoney`, `ProcessUpdateTraderState`.

### Important distinction

These inbound/update handlers are **not sell requests**.

Never invoke `ProcessRemoveItem` or update handlers to simulate sale. The server remains authoritative.

---

## 10. Why Auto Sell must mutate one current instance at a time

Wrong:

```text
scan bag once
 -> save 70 slots/IDs
 -> blast 70 sell requests
```

Risks:

- item list can be compacted/reordered;
- instance may disappear/change site;
- shop/server state may reject or update asynchronously;
- stale policy data can cause unintended mutation.

Correct loop:

```text
SCAN current bag
 -> filter candidates
 -> choose ONE current instance
 -> verify shop context + sellability
 -> send 200036 instanceID:NpcShopID:ShopID
 -> WAIT RemoveItem / UpdateItemsList / money/shop proof
 -> fresh SCAN
 -> choose next candidate
```

This removes the need for the old “press Sell 90 times” fallback architecture.

---

## 11. Bag item events — VERIFIED

`BagItemsGrid` renders 100 logical positions but populates them from:

`Game.GetItemsAtSite(Site)`.

Add/Remove/UpdateItemsList events refresh the structured grids.

Observed RemoveItem data carries enough identity context such as site/dbID/position for UI updates.

This supports event-driven or fresh-snapshot confirmation rather than screen inspection.

---

## 12. Item actions outside shop — VERIFIED examples

`CMD_ITEM_ACTION = 100005`.

Observed payload families:

- Equip -> `1:instanceID`
- Use -> `3:instanceID`
- Abandon -> `4:instanceID`
- Move -> `5:instanceID:destinationSite`
- Split -> `8:instanceID:quantity`.

Bag/site sort:

`CMD_BAG_SORT = 100006`.

Bag payload:

`10`.

Storage pages use site IDs 11..15.

Canonical storage detail:

`analysis/26_STORAGE_BANK_ITEM_MOVE.md`.

---

## 13. Ground loot integration

The client already has a semantic loot subsystem.

Typical source path:

```text
nearby ItemPack
 -> path/reachability
 -> ClickToObject
 -> pack contents
 -> item policy / bag capacity
 -> PickUpItemFromItemPack
 -> bag update
```

Therefore a sophisticated Auto Sell policy can share the same static Item/Equip classification with the loot filter rather than duplicating image/name heuristics.

Canonical detail:

`analysis/27_LOOT_PICKUP_FILTER_ENGINE.md`.

---

## 14. Auto Sell state machine

Recommended high-level flow:

```text
TRAINING
 -> observe GetFreeBagSpace
 -> threshold reached
 -> suspend Train
 -> choose configured/current-map vendor candidate
 -> semantic navigation to vendor
 -> open actual NPC/shop state
 -> verify current NpcShopID + ShopID
 -> scan current Bag
 -> filter ONE candidate
 -> send exact sell request
 -> wait server/item proof
 -> rescan/repeat
 -> stop when policy satisfied/no candidates/enough free slots
 -> leave shop
 -> return saved train location
 -> verify map/position
 -> resume Train
```

Do not let Shop, Train, Buff or other mutable actions run concurrently for the same PID.

---

## 15. Remaining targeted unknowns

The fundamental sell mechanism is solved. Remaining questions are policy/runtime details, not broad reverse tasks:

- which vendor/service NPC should be chosen on a specific map/profile;
- exact service opening path for a chosen NPC if not already observed;
- final user keep/sell/store policy;
- any special server restriction on unusual item classes;
- normalized upload/index of all large Item/Equip rows for fast AI lookup.

Do not re-reverse the shop packet or claim the Config item tables are still only predictions.
