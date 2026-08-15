# Global Lua helpers — reusable semantic functions

Status: **VERIFIED from decrypted `Global_Functions.lua` source**.

This file records high-value helper functions the game itself exposes. Future AI should inspect/reuse these before rebuilding equivalent flows externally.

## `GoToMap(mapID)`

Documented description: `Tự tìm đường đến bản đồ tương ứng`.

Implementation simply calls:

`Game.GoTo(mapID, -1, -1)`

The `-1,-1` coordinate convention means route to the requested map without specifying a final local coordinate.

## `GoToNPC(mapID, npcID)`

Documented description: **`Tự tìm đường đến và đối thoại với NPC tương ứng`**.

Exact flow:

### Different map

1. `Game.GoTo(mapID, -1, -1, callback)`
2. `npcPos = Game.GetNPCPosition(npcID)`
3. if `npcPos == nil`: `GUI.ShowNotification("Không tìm thấy NPC tương ứng")`, return
4. `Game.GoTo(mapID, npcPos.X, npcPos.Y, callback)`
5. `Game.ClickNPC(npcID)`

### Same map

1. `npcPos = Game.GetNPCPosition(npcID)`
2. nil check + notification
3. `Game.GoTo(mapID, npcPos.X, npcPos.Y, callback)`
4. `Game.ClickNPC(npcID)`

### Consequences

- NPC X/Y does **not** need to be manually configured when `GetNPCPosition` can resolve it.
- `Game.ClickNPC(npcID)` is the intended semantic final interaction, not a mouse simulation.
- This helper is an excellent basis for Auto Heal / Auto Sell / quest/NPC service flows.

## `GoToMonster(mapID, monsterID)`

Documented description: `Tự tìm đường đến và đánh quái tương ứng`.

Pattern:
- cross-map `Game.GoTo(mapID,-1,-1)` if required;
- `Game.GetMonsterPosition(monsterID)`;
- nil check (`Không tìm thấy quái vật tương ứng`);
- `Game.GoTo(mapID, monsterPos.X, monsterPos.Y, callback)`.

The built-in Auto Fight engine then provides richer target selection/chase/skill semantics.

## `GF_AutoFightMain()`

Exact implementation:

`GUI.FindUI("AutoFight_Main")`

and returns that service/UI object.

This is a useful semantic locator for the already-running Auto Fight main component and further supports avoiding blind native UIButton scanning.

## Other useful global helper families

The same file includes helpers for:
- displaying item/buff duration;
- item-name/color and signet data;
- skill tooltip and magic-attribute descriptions;
- select-skill/select-item/select-pet UIs;
- task descriptions and clickable task routes;
- role preview;
- typed input dialogs (`GF_ShowInputMoney`, `GF_ShowInputNumber`, `GF_ShowInputString`);
- chat actions;
- pet/equip/pneuma display logic.

These are mostly UI/service convenience helpers; inspect them only when the relevant feature needs exact behavior.

## Design guidance

For any new feature, search in this order:

1. `Global_Functions` helper;
2. feature-specific Lua class;
3. Config/layout semantic data;
4. Game/Lua API bridge;
5. native disassembly only if the semantics remain unknown.
