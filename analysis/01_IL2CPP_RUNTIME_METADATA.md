# IL2CPP runtime + metadata

## Status

Phần này chủ yếu là **VERIFIED bằng binary/metadata inspection**. Những mapping field/method cụ thể chưa được runtime test sẽ được ghi rõ.

## 1. GameAssembly.dll là gì trong client này

`Game/GameAssembly.dll` là PE32+ x64 chứa native code do IL2CPP sinh ra cho các managed assemblies của game. Phân tích PE của snapshot hiện tại cho thấy:

- architecture: x86-64;
- image base: `0x180000000`;
- 7 PE sections;
- PE timestamp: 2026-06-28 UTC (chỉ là timestamp trong PE, không nên coi là ngày phát hành chính thức);
- chứa lượng lớn export `il2cpp_*`.

`ScriptingAssemblies.json` cho biết managed source set trước khi IL2CPP gồm ít nhất:

- `Assembly-CSharp.dll`
- `Assembly-CSharp-firstpass.dll`
- `LiveKit.dll`
- `Google.Protobuf.dll`
- `protobuf-net.dll`
- `Newtonsoft.Json.dll`
- `Unity.Burst.dll`
- `Unity.Collections.dll`
- nhiều `UnityEngine.*`
- URP/RenderPipeline assemblies
- Unity Purchasing/Services.

Điều này giải thích vì sao `GameAssembly.dll` chứa cả gameplay, protobuf/network glue, Lua bridge và nhiều Unity-managed wrapper.

## 2. IL2CPP API được export rất rộng

Snapshot hiện tại lộ khoảng **242 export bắt đầu bằng `il2cpp_`**. Nhóm quan trọng cho một runtime schema inspector gồm:

### Domain / assembly / image

- `il2cpp_domain_get`
- `il2cpp_domain_get_assemblies`
- `il2cpp_assembly_get_image`
- `il2cpp_image_get_name`
- `il2cpp_image_get_class_count`
- `il2cpp_image_get_class`

### Class/type

- `il2cpp_class_get_name`
- `il2cpp_class_get_namespace`
- `il2cpp_class_get_parent`
- `il2cpp_class_get_fields`
- `il2cpp_class_get_methods`
- `il2cpp_class_get_properties`
- `il2cpp_class_get_method_from_name`
- `il2cpp_class_get_field_from_name`
- `il2cpp_class_get_static_field_data`
- `il2cpp_class_from_name`
- `il2cpp_object_get_class`

### Field

- `il2cpp_field_get_name`
- `il2cpp_field_get_offset`
- `il2cpp_field_get_type`
- `il2cpp_field_get_value`
- `il2cpp_field_static_get_value`

### Method

- `il2cpp_method_get_name`
- parameter/return-type related APIs
- token/flags related APIs
- `il2cpp_runtime_invoke`

### Object / GC / handle

- `il2cpp_object_new`
- `il2cpp_object_unbox`
- `il2cpp_gc_foreach_heap`
- GC handle APIs

### Thread / icall

- thread attach/detach APIs
- `il2cpp_resolve_icall`

### Ý nghĩa thực tế

Tool không nhất thiết phải hardcode kiểu:

`GameAssembly.dll + 0x123456 = GetFreeBagSpace`

Có thể dựng resolver:

`domain -> image -> namespace -> class -> method/field -> native MethodInfo/offset`

RVA vẫn hữu ích khi disassemble, nhưng không nên là identity chính của method.

## 3. global-metadata.dat

File hiện tại:

- size: 14,747,552 bytes;
- magic đầu file: `AF 1B B1 FA`;
- metadata version field: **39**.

Parser cũ cho metadata IL2CPP version thấp có thể đọc sai header v39. Inspection snapshot hiện tại cho thấy header có cấu trúc mới/compact hơn và nhiều bảng có thể hiểu dưới dạng bộ `(offset, byteSize, count)`.

Các số đã suy ra có tính nhất quán cao:

- khoảng **16,080 type definitions**;
- khoảng **96 image records**;
- khoảng **96 assembly records**;
- khoảng **132,486 method records**;
- khoảng **69,661 field records**;
- khoảng **138,190 parameter records**;
- string heap trên 2 MB, hơn 116k string entries theo cách tách null-string.

Các con số này là cấu trúc metadata, không có nghĩa game có 132k gameplay methods; phần lớn đến từ Unity/.NET/support assemblies.

## 4. Image/assembly mapping đã kiểm tra

Candidate image table được kiểm tra bằng cách resolve name index vào string heap. Các record đầu trả về tên hợp lý như:

- `mscorlib.dll`
- `Assembly-CSharp.dll`
- `UnityEngine.UIElementsModule.dll`
- `LiveKit.dll`

Đây là bằng chứng tốt rằng parser đã đặt đúng vùng image definitions, dù exact layout của tất cả field trong record v39 vẫn cần parser chuyên biệt nếu muốn dump tự động hoàn chỉnh.

## 5. String heap là nguồn tri thức cực mạnh

Ngay cả trước khi hoàn thiện full metadata parser, string heap cho phép định vị các cụm class/method rất rõ:

- `MainGame`
- `FGStudio.LuaSystem.LuaSystemManager`
- `FGStudio.LuaSystem.LuaSystemSharedData`
- `LuaSystemAPI_Game`
- `LuaSystemAPI_GUI`
- `LuaSystemAPI_Network`
- `FGStudio.Engine.Objects.GScene`
- `NPCData`, `MonsterData`, `PortalData`, `ZoneData`
- item/buff/skill/network command strings.

Do IL2CPP metadata thường giữ name/namespace/member names, đây là phương án rất tốt để AI tra cứu subsystem mà không phải disassemble cả 62 MB GameAssembly từ đầu.

## 6. Một số concrete subsystem cluster trong Assembly-CSharp

String clustering cho thấy các tên sau nằm gần nhau và có quan hệ logic mạnh:

### LuaSystemManager

- `CreateTable`
- `OnReceiveEvent`
- `OnReceivePacket`
- `SendPacketToServer`
- `HasScript`
- `GetScript`
- `LoadFromAssetBundle`
- `LoadFromFolder`
- `ExecuteFunction`
- `LuaEnv`
- `Reload`
- `RegisterLibraries`
- `RegisterConstants`

### LuaSystemSharedData

- `GetNearestItemPack`
- `GetNearestNPC`
- `GetNearbySprites`
- `GetNearbyTeamLeaders`
- `GetNearTeammates`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyItemPack`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetItems`
- `FindItems`
- `FindItem`
- `GetItemsAtSite`

Đây là lý do `LuaSystemSharedData` hiện được đánh giá là một trong các entry point quan trọng nhất cho scanner.

## 7. Runtime invocation và main-thread

`il2cpp_runtime_invoke` tồn tại không có nghĩa mọi Unity method có thể gọi từ bất kỳ thread nào.

Cần phân biệt:

- **metadata/read-only queries**: thường có thể thực hiện an toàn hơn nếu chỉ inspect runtime structures;
- **Unity object/UI/action mutation**: phải giả định yêu cầu Unity main thread cho tới khi chứng minh ngược lại.

Một lỗi kiến trúc thường gặp là worker/native thread gọi thẳng code Unity. Điều này có thể chạy được vài lần rồi crash/disconnect vì method đụng GameObject, MonoBehaviour, Lua runtime hoặc PlayerLoop state.

## 8. Mô hình resolver được khuyến nghị

```text
IL2CPP Resolver
  -> find Assembly-CSharp image
  -> find namespace/class
  -> enumerate methods/fields
  -> cache stable semantic identifiers
  -> expose MethodInfo / field offset

Read-only Scanner
  -> inspect concrete objects/state

Main-thread Dispatcher
  -> execute validated game action
```

Cache nên dựa trên `(assembly, namespace, class, method, parameter count/signature)` thay vì chỉ RVA.

## 9. Những điều CHƯA được coi là verified

- Exact class chứa LocalPlayer/RoleData chính.
- Exact field offset cho HP/MaxHP/RoleID trong entity object.
- Exact memory owner của global nearby entity list.
- Exact signature/parameter types của mọi method chỉ tìm thấy qua string heap.
- Exact v39 metadata record layout cho mọi table.

AI sau này **không cần phân tích lại toàn bộ binary** để tìm những hướng này; hãy bắt đầu từ symbol clusters/document này, rồi chỉ verify phần exact layout cần cho task cụ thể.
