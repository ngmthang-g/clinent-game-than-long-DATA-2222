# 40 — Trade / item consolidation runtime stack

Status: **VERIFIED from shipped `OtherRolePopup.lua`, `Trade.lua`, `RoleInfo_BagTab.lua`, constants and TCP definitions/handler.** This document separates the protocol/session truth from any tool-specific batching policy.

## 1. Start trade by RoleID

Packet: `CMD_OTHER_ROLE_COMMAND = 200051`.

Constants: `C_OtherRoleCommand.Trade = 7`, `C_TradeCommand.Request = 1`.

Exact invitation payload emitted by shipped UI:

`7:1:targetRoleID`.

This is the semantic replacement for coordinate-clicking the selected-player popup when a trusted target RoleID is already known.

## 2. Active trade session

Session packet: `CMD_TRADE_DATA = 200053`.

Exact `C_TradeCommand` values:

- None 0
- Request 1
- Cancel 4
- AddItem 5
- RemoveItem 6
- UpdateMoney 7
- ChangeLock 8
- AddPet 9
- ClearPet 10
- Done 11.

`Trade:LoadData(data)` closes when `data == "-1"`; otherwise runtime trade state exposes at least:

`ExchangeID, RequestRoleID, AgreeRoleID, ItemsTrade[RoleID], MoneyDict, PetDict, LockDict, DoneDict`.

## 3. Exact session payloads

Every mutation uses the current local RoleID and current ExchangeID:

- lock/change lock: `roleID:8:exchangeID`
- remove item: `roleID:6:exchangeID:itemInstanceID`
- done: `roleID:11:exchangeID`
- money: `roleID:7:exchangeID:value`
- add item: `roleID:5:exchangeID:itemInstanceID`
- cancel: `roleID:4:exchangeID`
- add pet: `roleID:9:exchangeID:petDbID`
- clear pet: `roleID:10:exchangeID`.

Use live `dbItemData.ID` (instance ID), not ItemID/template ID or bag Position.

## 4. Nine-item capacity

`Trade.lua` defines `MaxItemCount = 9` and constructs 9 source + 9 destination item slots. This verifies **UI/session capacity of 9 item slots per side**.

It does **not** prove that “one round succeeded with 9 items”. Tool batching must prove current `ItemsTrade`, lock/done states, then final session close and fresh bag changes before starting another batch.

Bag UI only offers “Đặt lên” for `dbItemData.Bound == false`, so bound items must not be selected as transferable candidates.

## 5. Lock/done lifecycle

Local unlocked state exposes lock and money editing; after lock, Done becomes available and money editing is disabled. The UI indicates both sides locked before final completion and shows a 1% fee; the server remains authoritative for acceptance and actual money/item transfer.

## 6. Correct consolidation architecture

Recommended batch loop:

`fresh CON bag + fresh MAIN capacity -> select <=9 current unbound live instances -> request trade by MAIN RoleID -> wait active ExchangeID -> add items one by one -> verify ItemsTrade -> lock CON -> verify LockDict -> lock MAIN -> verify both locked -> Done each side -> wait CMD_TRADE_DATA close/state completion -> fresh MAIN/CON bag snapshots -> decide whether another batch is needed`.

Never infer repeat from a stale “free slots before trade” number alone. Never reuse old instance IDs after any completed trade because bag position/instance state may have changed.
