# Lua runtime, Game API, GUI API và Network API

## 1. Vì sao Lua layer là trung tâm

Binary/metadata cho thấy client không chỉ có C# gameplay. Nó có một Lua subsystem rõ ràng dưới `FGStudio.LuaSystem`. C# cung cấp bridge cấp cao để Lua query data, mở/tìm UI, gọi game action và gửi packet.

Điều này giải thích vì sao một số hành động nhìn như “nút UI” nhưng thực tế flow đúng có thể là:

```text
C# game state
 -> Lua API
 -> Lua script/UI
 -> network request
 -> server response
 -> C# process event/update state
```

Vì thế replay action nên quan sát cả **UI lifecycle + Lua callback + network event**, không chỉ `UIButton.HandleClickEvent`.

## 2. LuaSystemManager

Class đã thấy: `FGStudio.LuaSystem.LuaSystemManager`.

Các member/string quan trọng:

- `CreateTable`
- `OnReceiveEvent`
- `OnReceivePacket`
- `SendPacketToServer`
- `HasScript`
- `GetScript`
- `LoadFromAssetBundle`
- `LoadFromFolder`
- `ExecuteFunction`
- `get_LuaEnv` / `set_LuaEnv`
- `Reload`
- `RegisterLibraries`
- `RegisterConstants`

### Diễn giải

`LuaSystemManager` có vẻ là owner/bridge chính của Lua runtime. `HasScript`/`GetScript` rất có giá trị để xác nhận một UI/script đã thực sự được load, thay vì sleep cố định.

`LoadFromAssetBundle` củng cố giả thuyết rằng phần script/UI cụ thể có thể nằm trong `Interface.unity3d` hoặc bundle khác.

`OnReceivePacket`/`OnReceiveEvent` + `SendPacketToServer` cho thấy Lua có cả inbound và outbound network bridge.

## 3. LuaSystemSharedData — lớp query đáng ưu tiên nhất

Các query đã thấy:

- `get_LeaderRoleData` / `set_LeaderRoleData`
- `GetNearestItemPack`
- `GetNearestNPC(npcResID)`
- `GetNearbySprites(includeDeath)`
- `GetNearbyTeamLeaders`
- `GetNearTeammates(includeNonePlayers, lowHPPriority, maxTargets)`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyItemPack`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetDeviceInfo`
- `GetItems`
- `FindItems`
- `FindItem`
- `GetItemsAtSite(site)`

Compiler-generated lambdas quanh subsystem này nhắc tới:

- `npcData`
- `monsterData`
- `petData`
- `markData`
- `growPointData`
- `portalData`
- `zoneData`

### Ý nghĩa

Đây là bằng chứng mạnh rằng client đã có **query layer chuẩn hóa cho world objects**, không cần scan toàn RAM để đoán entity base.

Một scanner nên thử resolve/invoke read-only các query này trước khi xây custom heap scanner.

## 4. LuaSystemAPI_Game

Class này có phạm vi rất rộng. Danh mục dưới đây được lấy từ metadata/string cluster; exact signature của mọi method cần metadata parser hoặc runtime inspect nếu dùng thật.

### Skill / ability

- `GetAbilities`
- `GetAbilityLevel`
- `GetAbilityTemplateData`
- `GetAbilityName`
- `GetAbilityDescription`
- `GetAbilityIcon`
- `GetAbilityLevelUpExp`
- recipe-related getters
- `UseSkill(skillID)`
- `RequestUsingSkill`
- `RequestUsingSkillWithPos`
- `RequestUsingSkillWithTarget`
- `GetSkillLuaData`
- `IsSkillRequireTarget`

### NPC / object / target

- `ClickNPC(npcID)`
- `ClickToObject`
- `SelectTarget`
- `IsSelectTargetDie`
- `get_CurrentChaseTargetID`
- `ChaseTarget`
- `BugTarget`
- `IsAllowDeadTarget`

### Movement / navigation

- `DoLeap`
- `DoJump`
- `DoMeditate`
- `DoAction(actionID)`
- `StopAutoPath`
- `CanMove`
- `IsMoving`
- `get_IsMovingWithJoyStick`
- `HasPath(fromPos,toPos)`
- `CellToDistance`
- `CalculatePointOnLine`
- `GetDistance`
- `RangerRequest`
- strings/lambdas liên quan `MoveToEx`, `GoTo`.

### Auto / state

- `get_EnableAutoF1`
- `set_EnableAutoF1`
- `AutoRemoveFlag`
- `RangerAuto`
- `AutoSetFlag`
- `IsRoleBusy`
- `IsLastActionOver`
- `CanUseSkill`
- `CanUseItem`
- `IsProgress`

### Character / state

- `GetCurrentHP`
- faction functions
- appearance/avatar/hair/face/fashion functions
- `ChangeName`

### Buff

- `GetBuffs`
- `GetBuffProperties`
- `HasBuff`
- `GetBuffData`
- `GetTargetBuffIcons`
- `SendRemoveBuff(buffID)`

### Inventory/item

- `GetFreeBagSpace`
- `GetTotalItems`
- `GetItemTemplateData`
- `GetItemData(dbID)`
- `GetItemAtSite`
- `CountItem`
- `GetItemType`
- `GetEquipType`
- `GetPetEquipType`
- `GetItemIcon`
- `GetItemName`
- `GetEquipVisualID`
- `GetEquipStar`
- `GetEquipLevel`
- `GetEquipEnhanceData`
- `GetEquipIdentifyValue`
- `GetFakeItemData`
- `IsItemThrowable`
- `IsItemSellable`
- `IsItemSellToShopWithBoundMoney`
- `GetItemBasePrice`
- `GetItemBuyPrice`
- `GetItemMaxStack`
- `GetEquipSet`
- `GetPetEquipSet`
- `GetGemType`
- `GetGemLevel`
- `IsUniversalGem`
- `PickUpItemFromItemPack(itemPackID, slotIndex, UsingAuto)`

### Misc

- `DisplayTemporaryFx`
- `DisplayChat`
- `SendAnswerCaptcha`
- `OpenURL`
- `get_CoreVersion`
- `CheckCondition`
- `LuaCallback`

## 5. ClickNPC là entry point đặc biệt giá trị

Phân tích disassembly trước đó trên đúng snapshot này cho thấy `LuaSystemAPI_Game.ClickNPC(npcID)` đi theo logic tương đương:

```text
StopAutoPath
 -> locate NPC/object
 -> orient character toward NPC
 -> GScene.SelectTarget
 -> TCPGameEventProcessor.SendClickOnObject(objectID)
```

RVA đã từng quan sát ở snapshot này khoảng `0x66ADC0`, nhưng **RVA chỉ là evidence/debug hint, không phải identity lâu dài**.

### Kết luận

`ClickNPC` gần với hành động “người chơi click NPC thật” hơn nhiều so với gửi mouse click giả.

## 6. LuaSystemAPI_GUI

Các member đã thấy:

- `Instantiate`
- `MainCallUI`
- `MainFindUI`
- `MainFindAllUIs`
- `CallUI`
- `CallUIAlwaysOnTop`
- `FindUI`
- `FindAllUIs`
- `get_ImageMaterial`
- `ShowMessageBox(showCancel, showOK)`
- `ShowWaitingBox` (string evidence)

Disassembly trước đó cho `MainCallUI`/`CallUI` cho thấy chúng đi qua các thành phần kiểu:

- `MonoBehaviourExecutor.AddScript`
- `MonoBehaviourExecutor.GetScript`
- `MonoBehaviourExecutor.GetScriptUIRoot`

RVA từng quan sát trong snapshot:

- `MainCallUI` ~ `0x6A5E70`
- `CallUI` ~ `0x6A5CD0`
- `MainFindUI` ~ `0x6A5F90`
- `FindUI` ~ `0x6A5DF0`

Các RVA này dùng để đối chiếu disassembly, không nên hardcode vào tool cuối.

## 7. UIButton.HandleClickEvent — cảnh báo quan trọng

Đã thấy `FGStudio.LuaSystem.GUI.UIButton.HandleClickEvent`.

Disassembly trước đó cho thấy đây là **instance method** và native code dereference state từ `this` (đã thấy access quanh vùng kiểu `this + 0x100`).

Do đó các kiểu sau nguy hiểm:

- gọi method với `this = null`;
- lấy pointer UIButton ở UI state cũ rồi reuse sau khi panel đổi;
- cache pointer button lâu dài qua loading/map/UI reconstruction;
- gọi từ worker thread không phải Unity main thread.

Đây là lời giải thích rất hợp lý cho pattern lỗi từng thấy: bước đầu click được, panel đổi, bước sau pointer cũ không còn hợp lệ.

### Pattern đúng hơn

```text
perform action A
 -> WAIT condition/state
 -> FindUI / HasScript / query current UI
 -> resolve current instance/action B
 -> dispatch on main thread
 -> observe resulting state
```

Không dùng `Sleep(200)` như bằng chứng UI đã sẵn sàng.

## 8. LuaSystemAPI_Network

Đã thấy `SendPacket` trong `LuaSystemAPI_Network`.

Disassembly trước đó cho thấy bridge xuống:

`LuaSystemManager.SendPacketToServer(packetID, data)`.

RVA `SendPacket` từng quan sát khoảng `0x6A69A0` trên snapshot này.

### Ý nghĩa

Đây là điểm trace rất mạnh. Khi muốn hiểu một thao tác chưa rõ callback, ví dụ:

- NPC -> Trị liệu -> Đồng ý;
- NPC -> Mua bán -> Bán nhanh -> bán 1 item;

thì trace một lần:

- `MainCallUI` / `CallUI`: `uiName`, args;
- `SendPacket`: packetID + payload;
- inbound processor/event sau đó;

sẽ chính xác hơn đoán tên nút.

## 9. Kiến trúc action engine đề xuất

```text
Action Request
 -> Safety Guard
 -> verify game state
 -> resolve semantic method/UI
 -> enqueue max 1 mutable action
 -> Unity/Main Thread Dispatcher
 -> execute internal action
 -> Observer waits for concrete result
 -> state machine advances
```

Ví dụ NPC:

```text
NeedNPCAction
 -> ClickNPC(npcID)
 -> WAIT NPC Lua UI exists
 -> find current script/UI
 -> invoke exact Lua action
 -> WAIT expected next UI/server event
```

## 10. Điều nên trace thay vì reverse lại

Nếu future AI cần tên callback chính xác cho một menu cụ thể mà docs chưa có, đừng mổ toàn bộ GameAssembly lại. Trace targeted:

1. `LuaSystemAPI_GUI.MainCallUI`
2. `LuaSystemAPI_GUI.CallUI`
3. `LuaSystemManager.HasScript/GetScript`
4. `LuaSystemAPI_Network.SendPacket`
5. relevant inbound processor

Chỉ cần một thao tác manual đúng là có thể map end-to-end flow.

## 11. Phân loại mức chắc chắn

**VERIFIED/strong binary evidence:** các class/method names, existence of Lua bridges, instance nature of UIButton, ClickNPC flow đã disassemble trong snapshot, SendPacket bridge.

**PROBABLE:** UI treatment/shop action cụ thể sống trong Lua script/bundle; high-level UI state can be driven without blind coordinate clicks.

**NOT YET VERIFIED:** exact Lua function names/payloads cho `Trị liệu`, `Bán nhanh`, `Đầu thai`, `Đánh quái` ở UI hiện tại.
