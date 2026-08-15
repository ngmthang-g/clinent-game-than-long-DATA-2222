# Task / Quest runtime schema and built-in Auto Quest

Status: **VERIFIED from decrypted `Task*.lua`, `MiniBox_MiniTaskFrame.lua`, `Global_Functions.lua`, `AutoFight_Main.lua`, `TCPPacketDefine.lua`, `TCPCmdEventHandler.lua`.**

This client already contains a real quest/task semantic layer and a partially complete built-in Auto Quest engine. Future AI should inspect these paths before attempting OCR/pixel/task-text scraping.

## Exact task type constants

`C_TaskType`:

| Type | Value | Meaning |
|---|---:|---|
| Delivery | 0 | đưa tin / giao vật phẩm |
| KillMonster | 1 | giết quái |
| LootItemFromMonster | 2 | giết quái lấy vật phẩm |
| CollectItem | 3 | thu thập vật phẩm |
| EnterArea | 4 | đến khu vực |
| TransferNPC | 5 | hộ tống/chuyển NPC |
| LevelUp | 6 | đạt cấp |
| CapturePet | 7 | bắt trân thú |
| JoinFaction | 8 | gia nhập môn phái |
| CallFightPet | 9 | xuất chiến pet |
| UseItem | 10 | sử dụng vật phẩm |
| CraftItem | 11 | chế tạo vật phẩm |

## Runtime task APIs

The shipped Task UI uses:

- `Game.GetDoingTasks()`
- `Game.GetCanReceiveTasks()`
- `Game.GetTaskTemplateData(taskID)`
- `Game.GetTaskRule(taskID)`
- `Game.GetTaskName(taskID)`
- `Game.GetTaskRequireLevel(taskID)`
- `Game.SendAbandonTask(taskID)`.

For each active `dbTaskData`, the client directly uses:

- `dbTaskData.TaskID`
- `dbTaskData.Parameters`.

The exact shape of `Parameters` depends on TaskType and is used as server-updated progress state.

## Task template data fields proven by shipped UI/helpers

Depending on TaskType, the template exposes structured sections such as:

- `OfferNPC.MapID / NPCID`
- `DeliveryData.MapID / NPCID / Items`
- `KillMonsterData.MapID / Monsters[]`
- `LootItemFromMonsterData.MapID / Monsters[]`
- `CollectItemData.Items[]`
- `EnterAreaData.MapID / EnterAreas[]` with PosX/PosY
- `TransferNPCData.MapID / NPCID`
- `CompleteNPC.MapID / NPCID`
- `LevelUpData.Level`
- `CapturePetData.PetID`
- `JoinFactionData.FactionID`
- `CallFightPetData.PetID`
- `UseItemData.MapID / PosX / PosY / ItemID / Quantity`
- `CraftItemData.ItemID / Quantity`
- `NextTaskID`
- `TaskRule`
- reward fields used by Task UI.

This is far richer than parsing the visible Vietnamese quest description.

## Clickable task descriptions already contain semantic navigation callbacks

`GF_GetTaskDescription(taskData, dbTaskData)` and `GF_GetMiniTaskDescription(...)` generate both human-readable text and semantic click handlers.

The helpers use:

- `GoToNPC(mapID,npcID)`
- `GoToMonster(mapID,monsterID)`
- `Game.GoTo(mapID,x,y)`
- direct item/template lookups.

The mini task frame stores the generated callback directly in the task UI Tag and invokes it when the user clicks the task.

### Consequence

A future quest helper does not need to parse colored task text to determine a destination. The same structured template/progress data used to build the text already describes where to go and what to do.

## Built-in Auto Quest selection logic

`AutoFight_Main:GetTaskCanAuToTask()` reads `Game.GetDoingTasks()` and chooses a task whose:

- template exists;
- `NextTaskID != -1`;
- TaskType is not CollectItem.

It prefers `TaskRule == 0`; otherwise it keeps another suitable candidate.

This means the game's built-in quest automation intentionally supports a subset of active tasks and excludes CollectItem from its automatic candidate selection.

## Exact built-in Auto Quest engine

`AutoFight_Main:AutoMainQuest()` runs a coroutine with state guards:

- stop when Auto mode becomes None;
- stop when local player dies;
- wait during `Game.IsProgress()`;
- wait while `Game.IsMoving()`;
- run auto HP recovery periodically;
- do not issue another quest action while a current GameDialog or monster-kill subtask is active.

### Delivery

Uses `GoToNPC(DeliveryData.MapID, DeliveryData.NPCID)`.

### CallFightPet

Checks `CurrentTaskData.Parameters[1]`.

If not complete:

- chooses first pet;
- sends `CMD_PET_ACTION` with `C_PetAction.CallFight:PetID`;
- waits and reloads task state.

If complete: goes to `CompleteNPC`.

### KillMonster

For each configured monster:

- reads required Count;
- reads `CurrentTaskData.Parameters[MonsterID]` as completed count;
- if incomplete, sets current required monster and calls `GoToMonster(MapID,MonsterID)`;
- when all are complete, goes to `CompleteNPC`.

### LootItemFromMonster

Groups required items by MonsterID.

Progress is checked using the **actual bag count**:

`Game.GetTotalItems(C_ItemSite.Bag, ItemID)`.

If an item is still needed, it goes to the relevant monster and starts the train combat logic. When requirements are satisfied, it goes to CompleteNPC.

### JoinFaction

Checks `Game.RoleData.FactionID` directly. If requirement is not met, it displays a user notification and stops Auto. If met, it goes to CompleteNPC.

### LevelUp

Checks `Game.RoleData.Level`. If too low, it notifies the user and stops Auto rather than attempting an invalid action.

### EnterArea

Uses `CurrentTaskData.Parameters[idx]` as completion flag. If incomplete:

- computes distance to `areaInfo.PosX/PosY`;
- can mount;
- calls `Game.GoTo(MapID,PosX,PosY)`.

Once complete, it proceeds to CompleteNPC.

## Auto Quest NPC interaction differs slightly from generic `GoToNPC`

`AutoFight_Main:GoToNPC()`:

1. routes to target map if needed;
2. gets `Game.GetNPCPosition(npcID)`;
3. moves within about 100 distance;
4. gets `Game.GetNearestNPC(npcID)`;
5. if no current GameDialog and timing guard allows, calls:

`Game.SelectTarget(NearestNPC.RoleID, true)`.

This is a valuable observation: in this quest path, `SelectTarget(RoleID,true)` is sufficient to trigger the expected NPC interaction/dialog behavior rather than explicitly calling `ClickNPC` in this function.

Future AI should preserve both known semantic interaction routes and choose based on the exact feature/source donor.

## Auto Quest monster flow

`GoToMonster(mapID,monsterID)` obtains `Game.GetMonsterPosition(monsterID,true)` and routes there. Once near the monster area it removes the auto flag and starts the normal Auto Train combat engine.

This demonstrates a composition pattern:

`Quest objective -> semantic navigation -> existing Auto Train engine -> progress event/task update -> next objective`.

## GameDialog auto-quest selection

`AutoFight_Main:ProcessGameDialog(gameDialogData)` waits for the dialog, then scans `Selections` for semantic text including:

- `[NHẬN]`
- `[TRẢ]`
- `Nhận thưởng`
- `Tiếp nhận`.

It sends the actual selection ID through:

`CMD_SHOW_GAMEDIALOG = 100007`.

If award item choice is enabled, it chooses an available award ItemID. Otherwise it submits the selection normally.

Fallback close/ack selection checks:

- `selectionID == 99999`, or
- text `Ta biết rồi`.

This is another strong precedent for **dynamic text-to-selection matching**, exactly like the recommended NPC Trị liệu approach.

## Task runtime events

`G_TCPEventType` task events are:

- `AssignTask = 20`
- `RemoveTask = 21`
- `UpdateTask = 22`.

### AssignTask

The event provides a `dbTaskData` object, adds it to MiniBox and tells `AutoFight_Main` to reload current task selection.

### RemoveTask

Data contains TaskID. MiniBox removes it; the main Task window is closed if open.

### UpdateTask

The event provides the updated `dbTaskData`, allowing progress UI/state to refresh.

These events are excellent task-state proof for a future quest controller.

## Recommended normalized task snapshot

```text
TaskID
TaskType
TaskRule
NextTaskID
TemplateData
Parameters
OfferNPC
CompleteNPC
Objective-specific data
LastUpdateTick
```

Keep template/static data cached by TaskID and copy only live progress data into per-process snapshots.

## Safe architecture for future quest automation

```text
Task Events / GetDoingTasks
 -> normalized Task Snapshot
 -> choose supported objective
 -> semantic navigation/action
 -> use existing Train/NPC/Pet subsystem
 -> wait Assign/Update/RemoveTask or GameDialog state
 -> rescan/reselect
```

Do not build quest automation by OCR-reading the mini quest text when structured TaskTemplate + DBTaskData already exist.

## Scope note

The built-in Auto Quest does not automatically solve every `C_TaskType` even though `GF_GetTaskDescription` supports describing/navigation for all 12 task types. Treat unsupported task types as feature-expansion candidates, not as already-verified full automation.