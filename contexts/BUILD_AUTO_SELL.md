# Context Pack — Build Auto Sell

## Scope

Use for bag-full detection, inventory filtering, vendor routing, opening shop, semantic sell requests and returning to Train.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
3. `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
4. `features/AUTO_SELL.md`
5. `analysis/12_GLOBAL_LUA_HELPERS.md`
6. `analysis/22_MAP_MINIMAP_RUNTIME.md`

## OPTIONAL

- Static item/equip classification: `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` + specific CSV chunk.
- NPC/vendor lookup: `database/README.md`, `database/NPC_SERVICE_CANDIDATES.md`, `database/npcs/`.
- MainThread execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.
- Orchestrator integration: `contexts/BUILD_ORCHESTRATOR.md`.

## VERIFIED bag truth

Use:

- `Game.GetFreeBagSpace()`;
- `Game.GetItemsAtSite(C_ItemSite.Bag)`;
- item `ID` = live instance ID;
- `ItemID` = template ID;
- `Position` = current slot;
- `Site` = logical container.

Do not count bag cells from pixels/UI to know whether the bag is full.

## Exact sell request

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

payload:

`itemInstanceID:NpcShopID:ShopID`.

Current `NpcShopID` and `ShopID` come from current shop state.

## Filtering guards

At minimum:

- block quest range `40000000 <= ItemID < 50000000` as shipped source does;
- require `Game.IsItemSellable(ItemID)`;
- honor user whitelist/keep policy;
- never confuse template ItemID with live instance ID.

For “keep weapons, sell other equipment”, static template slot truth is `EquipPoint == 0` = Weapon; runtime `GetItemType/GetEquipType` remains preferred for live decisions.

## Mutation-safe inner loop

`SCAN -> choose ONE current item instance -> SEND one sell -> WAIT RemoveItem/UpdateItemsList/shop-money proof -> RESCAN -> repeat`.

Do not pre-cache 90 slots or blindly click/sell 90 times.

## Vendor/NPC routing

Use semantic NPC/map data and `Game.GetNPCPosition` / `GoToNPC` patterns. Do not invent fixed X/Y from AutoPath NPCData.

## Shop state proof

Do not sell merely because an NPC was clicked. Wait for current NPCShop/shopData and reject incompatible shop states such as guild-shop sell-disabled state.

## Completion criteria

Auto Sell should stop when no current sell candidates remain or the configured free-space target is met, then return to saved Train map/position, verify map-ready/position state, and only then resume Train.