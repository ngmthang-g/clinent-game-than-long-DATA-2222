# VERIFIED findings — frozen client snapshot

> Chỉ chứa các fact có direct binary/metadata/disassembly/runtime evidence. Dự đoán nằm ở `PROBABLE.md` và `HYPOTHESES.md`.

## 1. Client là Unity x64 + IL2CPP

Status: **VERIFIED**

Evidence:

- `GameAssembly.dll` là PE32+ x64 IL2CPP native module.
- `global-metadata.dat` có IL2CPP metadata magic và version field `39`.
- `ScriptingAssemblies.json` liệt kê `Assembly-CSharp.dll`, `Assembly-CSharp-firstpass.dll` và Unity-managed assemblies.
- `data.unity3d` có `UnityFS` header và Unity version text `6000.3.6f1`.

Interpretation: gameplay managed code đã được IL2CPP compile vào `GameAssembly.dll`; metadata giữ semantic type/member information.

## 2. Snapshot repo khớp archive binary đã phân tích

Status: **VERIFIED**

`GameAssembly.dll` trong archive nghiên cứu có SHA-256 trùng LFS object ID của repo hiện tại. `global-metadata.dat` cũng trùng. Điều này xác nhận các phân tích binary hiện tại thuộc đúng snapshot trong repo.

Repo được chủ sở hữu coi là snapshot cố định, nên không cần workflow re-hash thường xuyên.

## 3. GameAssembly export IL2CPP API rất rộng

Status: **VERIFIED**

Inspection export table thấy khoảng 242 tên `il2cpp_*`, gồm các nhóm:

- domain/assembly/image enumeration;
- class name/namespace/field/method/property enumeration;
- field name/offset/type/value;
- method name/signature/token-related access;
- `il2cpp_runtime_invoke`;
- object/class APIs;
- `il2cpp_class_get_static_field_data`;
- `il2cpp_gc_foreach_heap`;
- thread attach/detach;
- internal-call resolution.

Consequence: có thể xây metadata-driven runtime resolver thay vì chỉ hardcode RVA.

## 4. Metadata v39 chứa quy mô type/method/field lớn và image table hợp lệ

Status: **VERIFIED bằng structural parsing**

Các bảng đã suy ra nhất quán:

- ~16,080 type definitions;
- 96 image records;
- 96 assembly records;
- ~132,486 method records;
- ~69,661 field records;
- ~138,190 parameter records.

Image table candidate đã resolve ra tên hợp lý: `mscorlib.dll`, `Assembly-CSharp.dll`, `UnityEngine.UIElementsModule.dll`, `LiveKit.dll`.

Exact layout mọi record v39 chưa được tuyên bố hoàn chỉnh.

## 5. Lua subsystem và các class bridge tồn tại

Status: **VERIFIED bằng metadata/string evidence**

Đã xác nhận symbol/class names:

- `FGStudio.LuaSystem.LuaSystemManager`
- `FGStudio.LuaSystem.LuaSystemSharedData`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Game`
- `FGStudio.LuaSystem.API.LuaSystemAPI_GUI`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Network`
- `FGStudio.LuaSystem.GUI.UIButton`

`LuaSystemManager` có các member name gồm `HasScript`, `GetScript`, `LoadFromAssetBundle`, `ExecuteFunction`, `OnReceivePacket`, `SendPacketToServer`.

## 6. LuaSystemSharedData có nearby world queries

Status: **VERIFIED về existence/name**

Các query names đã thấy:

- `GetNearestNPC`
- `GetNearbySprites`
- `GetNearbyTeamLeaders`
- `GetNearTeammates`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetNearestItemPack`
- `GetNearbyItemPack`
- `GetItems`
- `GetItemsAtSite`
- `FindItems`
- `FindItem`.

Return type/field layout chưa được mark VERIFIED.

## 7. `LuaSystemAPI_Game.ClickNPC(npcID)` có internal NPC click flow

Status: **VERIFIED bằng direct disassembly trên snapshot**

Observed flow:

```text
StopAutoPath
 -> find/resolve NPC object
 -> orient toward NPC
 -> GScene.SelectTarget
 -> TCPGameEventProcessor.SendClickOnObject(objectID)
```

Historic RVA hint: khoảng `0x66ADC0`.

Consequence: đây là game-internal NPC interaction entry point, không phải simulated mouse click.

## 8. `UIButton.HandleClickEvent` là instance method và dereference `this`

Status: **VERIFIED bằng direct disassembly**

Class: `FGStudio.LuaSystem.GUI.UIButton`

Method: `HandleClickEvent`

Native code đọc state từ object instance (đã quan sát access quanh region kiểu `this + 0x100`). Vì thế gọi với null/stale instance là không hợp lệ và có thể crash/no-op.

Historic RVA hint: khoảng `0x52D140`.

## 9. High-level Lua GUI APIs tồn tại

Status: **VERIFIED bằng metadata + disassembly trước đó**

- `MainCallUI`
- `CallUI`
- `MainFindUI`
- `FindUI`
- `MainFindAllUIs`
- `FindAllUIs`
- `CallUIAlwaysOnTop`
- `ShowMessageBox`

Disassembly `MainCallUI/CallUI` thấy call chain liên quan `MonoBehaviourExecutor.AddScript/GetScript/GetScriptUIRoot`.

Historic RVA hints nằm trong `database/API_QUICK_REFERENCE.md`.

## 10. Lua network send bridge tồn tại

Status: **VERIFIED bằng disassembly**

`LuaSystemAPI_Network.SendPacket(packetID, data)` chuyển xuống `LuaSystemManager.SendPacketToServer(packetID, data)`.

Historic RVA hint: khoảng `0x6A69A0`.

## 11. Inventory semantic API tồn tại

Status: **VERIFIED về symbol/API existence**

Đã thấy:

- `GetFreeBagSpace`
- `GetItems/GetItemsAtSite`
- `GetItemAtSite`
- `GetItemData`
- `GetItemType`
- `GetEquipType`
- `IsItemThrowable`
- `IsItemSellable`
- price/stack/equip/gem related methods.

`LuaItemData` member names đã thấy: `ID`, `ItemID`, `Site`, `Position`, `Bound`, `Quantity`, `Durability`.

## 12. Item và Equip categories có semantic names

Status: **VERIFIED về enum/member names**

Item types thấy: `Equip`, `CommonItem`, `Gem`, `Medicine`, `PetEquip`.

Equip types thấy gồm: `Weapon`, `Hat`, `Cloth`, `Gloves`, `Shoes`, `Belt`, `Ring`, `Necklace`, `Mount`, `Amulet`, `Cuff`, `Shoulderpads`, `Fashion`, `Dart`, `Soul`, `DragonTattoo`, `HeroicOrder`, `Signet`, `WeaponVisual` và variants.

Numeric values chưa được ghi là VERIFIED.

## 13. Shop/inventory state có server update handlers

Status: **VERIFIED về processing/command names**

Đã thấy các process/update names:

- `ProcessRemoveItem`
- `ProcessUpdateItemsList`
- `ProcessUpdateMoney`
- `ProcessUpdateTraderState`.

Cùng command names `CMD_REMOVE_ITEM`, `CMD_UPDATE_ITEMS_LIST`, `CMD_UPDATE_MONEY`, `CMD_UPDATE_TRADER_STATE`.

Consequence verified: các hàm `Process*` là processing/update side, không được coi mặc định là action request bán item.

## 14. World/scene/path classes tồn tại

Status: **VERIFIED về symbol existence**

Đã thấy:

- `FGStudio.Engine.Objects.GScene`
- `PathFinder`
- `NodeGrid`
- `LocalMapComponents`
- `NPCData`
- `MonsterData`
- `PortalData`
- `ZoneData`
- `GrowPointData`
- obstruction/region/safe-area names.

`GScene` có method names như `GetGroundHeight`, `InSafeArea`, `CanEnter`, `DoSyncPosition`, `DoVisionLogic`, `get_PathFinder`.

## 15. Skill/buff semantic APIs tồn tại

Status: **VERIFIED về symbol/API existence**

Đã thấy `UseSkill`, `RequestUsingSkill*`, `GetSkillLuaData`, `CanUseSkill`, `GetBuffs`, `HasBuff`, `GetBuffData`, `GetBuffProperties`, `GetTargetBuffIcons`, `SendRemoveBuff`.

## 16. Network command namespace chứa world/combat/inventory/revive/task events

Status: **VERIFIED về command names**

Đã thấy nhiều names, gồm:

- `CMD_CHANGE_MAP`
- `CMD_NEW_OBJECTS` / `CMD_REMOVE_OBJECTS`
- `CMD_CLICK_OBJECT`
- `CMD_REMOVE_ITEM` / `CMD_UPDATE_ITEMS_LIST`
- `CMD_USE_SKILL`
- `CMD_SKILL_DAMAGE` / `CMD_SKILL_HEAL`
- `CMD_OBJECT_DEATH`
- `CMD_REVIVE`
- `CMD_ADD/UPDATE/REMOVE_BUFF`
- task/pet/team/trader/chat/voice/client-Lua related commands.

Existence không tự xác định packet direction/payload.

## 17. FGClientTool_Windows.dll là custom asset transform module

Status: **VERIFIED bằng export/disassembly**

Exports:

- `FG_Encrypt`
- `FG_Decrypt`
- `HelloWorld`.

`FG_Decrypt` có direct checks cho `UnityFS`, `UnityRaw`, `UnityWeb`, có custom front/back byte transformations và một branch dùng constant `0x9E3779B9` + xorshift-derived parameters.

Consequence: file là chìa khóa thực tế để phục hồi asset bundle bị custom header/obfuscation.

## 18. data.unity3d là plain UnityFS bundle

Status: **VERIFIED bằng binary header**

`data.unity3d` bắt đầu `UnityFS` và chứa Unity version text `6000.3.6f1`.

Một số Interface/Config bundles dùng custom transformed header.

## 19. Launcher/Host là .NET Framework 4.7.2 components

Status: **VERIFIED bằng PE/CLR/config inspection**

- `Host.exe`: .NET console/helper updater/download/extract logic.
- `Launcher.exe`: WPF launcher; strings cho thấy account/process/session, sync group/master, recording/playback, server selection and launcher control service.

Đây là launcher/session layer, không phải gameplay IL2CPP layer.

## 20. Voice realtime dùng LiveKit

Status: **VERIFIED bằng Version.xml + modules**

`Version.xml` ghi `VoiceRealtime Enable="true" Backend="livekit"`; `livekit_ffi.dll` và `LiveKit.dll` có mặt.

Do đó `livekit_ffi.dll` được xếp ưu tiên thấp cho gameplay reverse.

## 21. Runtime observations về nearby player HP

Status: **VERIFIED trong các thử nghiệm trước trên client**

Đã quan sát một player khác (`CaoTốUyên`, RoleID sample `4030562`) có HP/MaxHP realtime và position được client giữ khi trong phạm vi quan sát, kể cả không dựa hoàn toàn vào team membership.

Điều này chứng minh client nhận một phần entity state của nearby players. Nó **không chứng minh toàn map visibility**; AOI vẫn là giới hạn.

## Quy tắc dùng file này

- Nếu một điều chỉ là suy ra từ tên, nhưng semantics chưa test: giữ ở `PROBABLE`.
- Nếu chỉ là hướng có thể tồn tại: giữ ở `HYPOTHESES`.
- Không biến historic RVA thành API contract.
- Không gọi response handler như request action.
