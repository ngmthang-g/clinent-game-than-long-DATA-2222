# Packet-driven UI lifecycle reference

Status: **VERIFIED from decrypted `TCPCmdHandler.lua` / `TCPCmdEventHandler.lua`.**

Use this file when an automation needs to know **what proves a UI/action state has actually arrived from the game/server**.

## Core rule

When an inbound packet/event drives a UI, prefer that packet/UI lifecycle as state proof over a fixed delay.

## `CMD_REVIVE_DATA = 200063` -> `Revival`

Inbound flow:

1. receive `revivalData`;
2. `GUI.FindUI("Revival")`;
3. if existing UI and data is nil or `Action == C_RevivalFrameAction.Close` -> destroy it;
4. if existing UI and still active -> `Revival:UpdateData(revivalData)`;
5. if absent and `Action == Open` -> `GUI.CallUI("Revival", revivalData)`;
6. find `AutoFight_Main` and call `DeathActive()`.

Strong state proofs:

- open: `Revival` exists and current server data says Open;
- update: same UI receives new revive data;
- close: server close action destroys UI;
- post-revive: wait additionally for RoleData/map/spawn state expected by the feature.

## `CMD_NPC_SHOP_DATA = 200034` -> `NPCShop`

Inbound flow:

1. `shopData = data`;
2. `GUI.FindUI("NPCShop")`;
3. if nil -> `GUI.CallUI("NPCShop", shopData)`;
4. otherwise -> `NPCShop:RefreshData(shopData)`.

Strong state proof for Auto Sell:

- do not assume shop is ready immediately after `ClickNPC`;
- wait until `NPCShop` exists / shop data arrives;
- use current `shopData`/shop identifiers when constructing sell actions.

## `CMD_SHOW_GAMEDIALOG = 100007` -> `GameDialog`

Inbound flow:

1. find old `GameDialog`;
2. destroy it if present;
3. if `data == "NULL"`, stop: no new dialog;
4. find `AutoFight_Main` and call `PutGameDialog(data)`;
5. `GUI.CallUI("GameDialog", data)`.

Strong state proof for NPC Trị liệu / task interactions:

- wait for actual GameDialog data;
- read `Selections` from the current data;
- choose by visible semantic text;
- send actual selection ID;
- observe next packet/UI state rather than sleeping blindly.

## `G_TCPEventType.AddBuff / RemoveBuff / UpdateBuff` -> `BuffFrame`

Event handler routes buff changes to the existing `BuffFrame`:

- Add -> `BuffFrame:AddBuff(dbBuffData)`
- Remove -> `BuffFrame:RemoveBuff(buffID)`
- Update -> `BuffFrame:UpdateBuff(dbBuffData.BuffID, dbBuffData.DurationTick, dbBuffData.Stack)`.

This proves buff updates are event-driven and include at least:

- BuffID
- DurationTick
- Stack

in the update event data consumed by Lua.

Potential state proof for buff automation: observe the corresponding buff/event data rather than relying only on cast animation.

## `G_TCPEventType.OpenPickUpItemFromItemPack`

The event includes item-pack ID/items and checks `AutoFight_Main:IsPickByAuto(itemPackID)`.

If the pack was initiated by Auto:

- auto service receives data through `RevicePackItemData(itemPackID, items)`.

Otherwise UI is opened/updated through `PickUpItem`.

This is useful for semantic loot confirmation.

## UI open/update pattern seen across the client

A recurring pattern is:

```text
ui = GUI.FindUI("Name")
if ui == nil:
    ui = GUI.CallUI("Name", data)
else:
    ui:RefreshData/LoadData/UpdateData(data)
```

This pattern occurs for NPCShop, friends, mail, guild, market, pet and many other systems.

For future automation, the script object returned by `FindUI` is generally a better semantic state handle than locating a child UIButton by native address.

## `MessageBox` is callback-driven, not packet-ID-driven

`GUI.ShowMessageBox(...)`/MessageBox instances store the caller's OK/Cancel delegates. Therefore generic confirmation state is different from GameDialog:

- identify the active MessageBox;
- understand who created it and what callback it carries when possible;
- semantic OK = `ButtonOKClicked()` -> destroy -> execute callback;
- do not assume every OK button sends the same packet.

## Recommended watcher model

For each mutable action maintain one expected transition, for example:

### Open shop

`ClickNPC -> WAIT CMD_NPC_SHOP_DATA / NPCShop exists -> READY`

### NPC dialog

`ClickNPC/SelectTarget -> WAIT CMD_SHOW_GAMEDIALOG -> read Selections`

### Revive

`death -> WAIT Revival Open -> send one revive action -> WAIT Revival Close + spawned state`

### Buff

`cast -> WAIT HP/buff/update event or validated cooldown/cast outcome`

## Guardrail

Inbound `Process*`, UI refresh methods and event handlers are **observers/state applicators**, not automatically valid request actions. Do not call a response/update handler to fake server state.
