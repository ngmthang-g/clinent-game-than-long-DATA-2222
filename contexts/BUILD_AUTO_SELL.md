# Context Pack — Build Auto Sell

## Scope

Use for bag-full detection, inventory filtering, vendor routing, opening shop, semantic sell requests and returning to Train.

## REQUIRED reading

1. `AI_BOOTSTRAP.md`
2. `AUTO_TOOL_SCOPE.md`
3. `features/AUTO_SELL.md`
4. `database/AUTO_SELL_CLASSIFICATION.md`
5. `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
6. `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`

## OPTIONAL — only when needed

- NPC movement/helper detail: `analysis/12_GLOBAL_LUA_HELPERS.md`, `analysis/22_MAP_MINIMAP_RUNTIME.md`.
- Vendor lookup: `database/README.md`, `database/NPC_SERVICE_CANDIDATES.md`, `database/npcs/`.
- Deep static schema/statistics: `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md`.
- Exact static rows/chunks: only if the required data has actually been materialized under `database/static/...`.
- MainThread execution: `contexts/BUILD_MAINTHREAD_BRIDGE.md`.
- Orchestrator integration: `contexts/BUILD_ORCHESTRATOR.md`.

Do not load all Items/Equips merely to implement one keep/sell rule.

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

Current `NpcShopID` and `ShopID` come from the current live shop state.

## Filtering guards

At minimum:

- block quest range `40000000 <= ItemID < 50000000` as shipped source does;
- require `Game.IsItemSellable(ItemID)`;
- honor explicit user keep/protected policy;
- never confuse template ItemID with live instance ID.

For “keep weapons”, static slot truth is:

`EquipPoint == 0` = Weapon.

Runtime `GetItemType/GetEquipType` remains preferred for live action-time classification.

Do **not** interpret “not Weapon” as automatically safe to sell. Medicine, gems, materials and special items require their own policy.

Canonical compact policy: `database/AUTO_SELL_CLASSIFICATION.md`.

## Mutation-safe inner loop

```text
fresh bag snapshot
 -> choose ONE current sellable instance
 -> SEND one sell
 -> WAIT RemoveItem / UpdateItemsList / consistent shop-money proof
 -> publish fresh bag snapshot
 -> re-run policy
```

Do not pre-cache 90 slots or blindly click/sell 90 times.

## Vendor/NPC routing

Use semantic NPC/map data and `Game.GetNPCPosition` / `GoToNPC` patterns. Do not invent fixed X/Y from AutoPath NPCData.

## Shop state proof

Do not sell merely because an NPC was clicked. Wait for current NPCShop/shopData and reject incompatible shop states such as guild-shop sell-disabled state.

## Completion criteria

Auto Sell should stop when:

- a fresh policy scan contains zero sell candidates; or
- the configured free-space target is reached.

Then return to saved Train map/position, verify alive + map-ready + position-in-tolerance, and only then resume Train.