# Bản đồ nghiên cứu client Thần Long

> Đây là tài liệu định hướng cấp cao cho AI. Đọc file này sau `AI_INDEX.md`, sau đó chỉ mở tài liệu subsystem liên quan. Repo được coi là một snapshot client cố định; mục tiêu là tránh reverse-engineer lại từ đầu ở các cuộc làm việc sau.

## 1. Kết luận kiến trúc lớn

Client là game Unity Windows x64 dùng IL2CPP. Logic gameplay C# đã được chuyển thành native trong `Game/GameAssembly.dll`, còn tên class/method/field/namespace và nhiều metadata cần thiết nằm trong `global-metadata.dat`. `ScriptingAssemblies.json` xác nhận có `Assembly-CSharp.dll`, `Assembly-CSharp-firstpass.dll`, `Google.Protobuf.dll`, `protobuf-net.dll`, `Newtonsoft.Json.dll`, `LiveKit.dll`, Unity Burst/Collections, URP và Unity Purchasing/Services.

Điểm quan trọng nhất: không nên nhìn client như một tập offset rời rạc. Dữ liệu cho thấy game có các lớp API cao cấp đủ để xây một framework gồm:

1. **Offline Game Database** — asset/config/map/NPC/item/skill/UI.
2. **Runtime Scanner** — đọc object/state thật: player, nearby entities, bag, buff, map, combat, UI.
3. **Internal Action Controller** — gọi action nội bộ đúng state/main-thread thay vì macro click mù.

## 2. Các nguồn tri thức quan trọng theo thứ tự ưu tiên

### P0 — Cực cao

- `Game/GameAssembly.dll`
  - gameplay IL2CPP native;
  - export rất nhiều `il2cpp_*` API;
  - chứa code của Assembly-CSharp và cầu nối C# ↔ Lua/UI/network;
  - là nguồn chính để tìm `LuaSystemManager`, `LuaSystemAPI_Game`, `LuaSystemAPI_GUI`, `LuaSystemSharedData`, `GScene`, item/buff/skill/network handlers.

- `Game/Thần Long  Mobile_Data/il2cpp_data/Metadata/global-metadata.dat`
  - metadata version 39;
  - khoảng 16.080 type definitions và 96 image/assembly records theo phân tích cấu trúc hiện tại;
  - là chìa khóa để map namespace/class/method/field mà không hardcode RVA.

- `Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`
  - ứng viên mạnh chứa bảng config tĩnh: NPC, map, item, skill, monster, quest, portal, magic/buff…;
  - cần giải mã/extract đúng bundle trước khi coi tên bảng cụ thể là VERIFIED.

- `Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll`
  - DLL riêng của game;
  - export `FG_Encrypt`, `FG_Decrypt`, `HelloWorld`;
  - code decrypt có nhận diện `UnityFS`, `UnityRaw`, `UnityWeb` và custom transform, rất quan trọng để bóc các bundle bị biến đổi.

### P1 — Rất cao

- `StreamingAssets/Interface.unity3d` và `StreamingAssets/Interface/*.unity3d`
  - nơi đáng đào để tìm UI prefab, Lua UI script/data, tên panel/button/callback, shared resources;
  - `Interface.unity3d` có header bị custom/obfuscate nhưng vẫn lộ dấu Unity bundle và version text.

- `Game/Thần Long  Mobile_Data/data.unity3d`
  - bundle UnityFS lớn (~47 MB), version text cho thấy Unity `6000.3.6f1`;
  - có thể chứa serialized game data/resources quan trọng.

- `RuntimeInitializeOnLoads.json`
  - xác nhận `Assembly-CSharp.SyncBootstrap.AutoInit` được gọi khi runtime khởi tạo;
  - có LiveKit/Burst/Unity Services init; hữu ích để hiểu bootstrap và main-thread environment.

### P2 — Trung bình

- `UnityPlayer.dll`: engine Unity, GameObject/Transform/PlayerLoop/AssetBundle/Input/rendering; cần khi bridge vào engine, nhưng gameplay chính không nằm ở đây.
- `lib_burst_generated.dll`: Burst compiled jobs, nhiều export bị hash; chỉ ưu tiên khi một subsystem cụ thể được chứng minh chạy qua Burst.
- `Thần Long  Mobile.exe`: Unity player executable, entry/bootstrap; ít gameplay trực tiếp.
- `Host.exe`, `Launcher.exe`: .NET Framework 4.7.2 launcher/update/multi-instance/control layer; hữu ích cho quy trình launch/update nhưng không phải nguồn gameplay chính.

### P3 — Thấp đối với gameplay

- `livekit_ffi.dll`: LiveKit/WebRTC voice/data/media stack. `Version.xml` xác nhận voice realtime backend là LiveKit.
- `baselib.dll`: Unity low-level memory/thread/socket/filesystem primitives.
- `D3D12Core.dll`: graphics runtime.
- `UnityCrashHandler64.exe`: crash collection.
- screenshots: chỉ có giá trị đối chiếu UI/visual, không phải nguồn logic.
- `*-resources.dat`: resource phụ của managed libraries, giá trị reverse gameplay thấp.

## 3. Subsystem đã thấy rõ trong metadata/string/binary

### Lua runtime và high-level API

Các class/namespace quan trọng đã thấy:

- `FGStudio.LuaSystem.LuaSystemManager`
- `FGStudio.LuaSystem.LuaSystemSharedData`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Game`
- `FGStudio.LuaSystem.API.LuaSystemAPI_GUI`
- `FGStudio.LuaSystem.API.LuaSystemAPI_Network`
- `FGStudio.LuaSystem.GUI.UIButton`

Đây là một phát hiện kiến trúc quan trọng: phần lớn flow UI/NPC/shop có thể đi qua Lua, trong khi C# cung cấp API cầu nối rất giàu chức năng.

### World/scene

Đã thấy `FGStudio.Engine.Objects.GScene`, `PathFinder`, `NodeGrid`, `LocalMapComponents`, `NPCData`, `MonsterData`, `PortalData`, `ZoneData`, `GrowPointData`, `MapAreaSoundData` và các nhóm obstruction/region/safe-area.

### Inventory/items

Đã thấy API trực tiếp cho free bag space, danh sách item, item instance/template, type/equip type, sellable/throwable, price, stack, bound, durability… Vì vậy inventory scanner không cần OCR/icon recognition.

### Combat/skill/buff

Đã thấy `UseSkill`, nhiều `RequestUsingSkill*`, buff getters/removal, target/combat helpers và một lượng lớn `magic_*` flags mô tả hiệu ứng kỹ năng/buff/debuff.

### Network/event

Đã thấy `SendPacket`, `SendPacketToServer`, `SendClickOnObject` và nhiều command/event như `CMD_CLICK_OBJECT`, `CMD_REMOVE_ITEM`, `CMD_UPDATE_ITEMS_LIST`, `CMD_USE_SKILL`, `CMD_OBJECT_DEATH`, `CMD_REVIVE`, `CMD_CHANGE_MAP`, `CMD_UPDATE_TRADER_STATE`, `CMD_CLIENT_LUA`…

## 4. Hai nguyên tắc để AI không suy luận sai

1. **Tên symbol tồn tại không đồng nghĩa action đã runtime-verified.** Ví dụ thấy `CMD_REVIVE` chứng minh protocol/event có khái niệm revive, nhưng chưa tự động chứng minh cách gửi packet revive chính xác.
2. **Response handler không phải request action.** Ví dụ `ProcessRemoveItem`/`ProcessUpdateMoney` là dấu hiệu server đã cập nhật client; không được gọi chúng để giả bán đồ.

## 5. Mục tiêu reverse đáng làm nhất nếu cần đào tiếp

Không ưu tiên tìm offset HP từng người. Ưu tiên tìm các object/query layer trung tâm đã có bằng chứng cụ thể:

- `LuaSystemSharedData` — nearby sprites/NPC/team/enemy/item pack/local map objects/inventory.
- `GScene` — scene, target, position, pathfinder, safe area, map components.
- Lua Game API — action/query layer cấp cao.
- Lua GUI API — panel/script lifecycle và callbacks.
- Lua Network API — packet bridge.

Các tên giả định kiểu `WorldManager`, `EntityManager`, `BagManager` chỉ nên dùng như mô hình tư duy; hiện chưa có bằng chứng phải tồn tại đúng tên đó.

## 6. Cách đọc knowledge base

- IL2CPP/metadata: `analysis/01_IL2CPP_RUNTIME_METADATA.md`
- Lua/API/UI/network: `analysis/02_LUA_GAME_UI_NETWORK_API.md`
- World/entity/map/path: `analysis/03_WORLD_ENTITY_MAP_PATH.md`
- Inventory/shop: `analysis/04_INVENTORY_ITEMS_SHOP.md`
- Combat/skill/buff: `analysis/05_COMBAT_SKILLS_BUFFS.md`
- Asset/encryption: `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md`
- Support modules/launcher: `analysis/07_SUPPORT_MODULES_LAUNCHER.md`
- Quick lookup: `database/API_QUICK_REFERENCE.md`
- Điều đã xác nhận: `research/VERIFIED.md`
- Dự đoán mạnh: `research/PROBABLE.md`
- Giả thuyết cần test: `research/HYPOTHESES.md`

## 7. Snapshot identity tối thiểu

Repo này được chủ động coi là snapshot cố định. Không bắt buộc workflow hash mỗi lần. Tuy nhiên binary trong archive nghiên cứu đã được đối chiếu với LFS object của repo cho `GameAssembly.dll` và `global-metadata.dat`, nên các phân tích dưới đây thuộc đúng snapshot hiện tại, không phải một client ngẫu nhiên khác.
