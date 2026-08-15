# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## Mục tiêu

Repo này là **canonical knowledge base** cho client Thần Long hiện tại. Client được coi là snapshot cố định; mục tiêu là để AI sau **đọc tài liệu trước, không reverse lại toàn bộ binary từ đầu**.

## Bắt buộc đọc theo thứ tự

1. `AI_INDEX.md` — file này.
2. `analysis/00_MASTER_RESEARCH_MAP.md` — bản đồ kiến trúc + ưu tiên file.
3. `research/VERIFIED.md` — các fact đã xác nhận.
4. Tài liệu subsystem đúng với task.
5. `database/API_QUICK_REFERENCE.md` khi cần tra symbol/method nhanh.
6. `research/PROBABLE.md` và `research/HYPOTHESES.md` khi cần hướng đào tiếp.

## Quy tắc quan trọng cho mọi AI

### 1. Không phân tích lại nếu tài liệu đã trả lời

Ví dụ nếu cần biết API inventory có gì, đọc:

- `analysis/04_INVENTORY_ITEMS_SHOP.md`
- `database/API_QUICK_REFERENCE.md`

Không dump lại toàn bộ GameAssembly chỉ để tìm `GetFreeBagSpace`.

### 2. Phân biệt mức chắc chắn

- **VERIFIED** — direct binary/metadata/disassembly/runtime evidence.
- **PROBABLE** — evidence mạnh, semantics chưa end-to-end verified.
- **HYPOTHESIS** — giả thuyết dùng để định hướng test.

Không được biến dự đoán thành fact chỉ vì nó “hợp lý”.

### 3. Repo là frozen snapshot

Chủ sở hữu không có kế hoạch thay client trong repo này. Không cần bắt user chạy hash/version check mỗi lần. Historic RVAs chỉ dùng để locate/debug; code cuối vẫn nên resolve semantic name khi có thể.

### 4. LFS pointer không phải binary

GitHub Contents API có thể trả về file text khoảng 130 byte cho `.dll/.exe/.dat` vì Git LFS. Deep binary analysis đã được thực hiện trên original bytes của archive khớp snapshot. Future AI có thể dùng docs trước; nếu cần disassembly mới, phải lấy original LFS bytes/local binary chứ không phân tích pointer text.

## Bản đồ tài liệu

### Architecture / file priority

`analysis/00_MASTER_RESEARCH_MAP.md`

- phân loại toàn bộ nhóm file;
- P0/P1/P2/P3 reverse-engineering value;
- kiến trúc Offline DB + Runtime Scanner + Internal Action Controller.

### IL2CPP / metadata

`analysis/01_IL2CPP_RUNTIME_METADATA.md`

- IL2CPP x64;
- metadata v39;
- ~16,080 type definitions, 96 images/assemblies;
- large `il2cpp_*` export surface;
- metadata-driven resolver strategy.

### Lua / UI / Network action bridge

`analysis/02_LUA_GAME_UI_NETWORK_API.md`

- `LuaSystemManager`;
- `LuaSystemSharedData`;
- `LuaSystemAPI_Game`;
- `LuaSystemAPI_GUI`;
- `LuaSystemAPI_Network`;
- `ClickNPC` flow;
- `UIButton.HandleClickEvent` stale-instance hazard;
- targeted tracing strategy cho callback/packet chưa biết.

### World / entities / maps / pathfinding

`analysis/03_WORLD_ENTITY_MAP_PATH.md`

- nearby sprite/object queries;
- `GScene`;
- `PathFinder`, `NodeGrid`;
- NPC/Monster/Portal/Zone data;
- AOI limitation;
- target/loot/NPC database possibilities.

### Inventory / items / shop

`analysis/04_INVENTORY_ITEMS_SHOP.md`

- bag APIs;
- `LuaItemData` ID vs ItemID vs Position;
- ItemType/EquipType;
- Weapon detection;
- safe filters;
- server-authoritative sell update;
- Auto Sell state machine.

### Combat / skills / buffs

`analysis/05_COMBAT_SKILLS_BUFFS.md`

- skill request APIs;
- buff query APIs;
- magic/effect flags;
- network combat commands;
- built-in Auto Fight evidence;
- buff-aware automation.

### Asset bundles / encryption

`analysis/06_ASSETS_ENCRYPTION_BUNDLES.md`

- `FGClientTool_Windows.dll`;
- `FG_Encrypt/FG_Decrypt`;
- UnityFS/UnityRaw/UnityWeb detection;
- `0x9E3779B9` xorshift branch;
- Config/Interface/data/Translations bundle roles.

### Support modules / launcher

`analysis/07_SUPPORT_MODULES_LAUNCHER.md`

- UnityPlayer;
- Burst;
- LiveKit;
- baselib/D3D12;
- Host/Launcher .NET stack;
- multi-instance/sync/record-playback evidence.

### Reusable quick lookup

`database/API_QUICK_REFERENCE.md`

- high-value class/method catalog;
- selected command names;
- item/equip categories;
- historic RVA hints.

## Các entry point quan trọng nhất hiện tại

### Runtime/world data

- `FGStudio.LuaSystem.LuaSystemSharedData`
  - `GetNearbySprites`
  - `GetNearbyObjects`
  - `GetLocalMapObjects`
  - `GetNearestNPC`
  - `GetNearByEnemies`
  - item queries.

### Scene/path

- `FGStudio.Engine.Objects.GScene`
- `PathFinder`
- `NodeGrid`

### Game actions

- `LuaSystemAPI_Game.ClickNPC`
- `SelectTarget`
- `UseSkill` / `RequestUsingSkill*`
- movement/state helpers.

### UI

- `LuaSystemAPI_GUI.MainCallUI/CallUI`
- `MainFindUI/FindUI`
- `LuaSystemManager.HasScript/GetScript`

### Network trace

- `LuaSystemAPI_Network.SendPacket`
- `LuaSystemManager.SendPacketToServer`

### Inventory

- `GetFreeBagSpace`
- `GetItemsAtSite`
- `GetItemType`
- `GetEquipType`
- `IsItemSellable`
- `IsItemThrowable`.

## Những việc KHÔNG nên lặp lại

- CE scan HP từng offset nếu mục tiêu có thể đạt qua SharedData/entity schema.
- dùng pixel/OCR để phân loại item khi data API tồn tại.
- gọi `UIButton.HandleClickEvent` như static/global function.
- reuse UIButton pointer sau khi UI transition.
- dùng fixed sleep làm state proof.
- gọi `ProcessRemoveItem`/response handler như action request.
- hardcode RVA làm identity duy nhất.
- reverse `livekit_ffi.dll`, `baselib.dll`, D3D12 trước gameplay modules.

## Khi gặp một tính năng chưa hoàn tất

### Nếu thiếu exact UI callback

Trace một thao tác manual tại:

- `MainCallUI/CallUI`;
- `HasScript/GetScript`;
- `SendPacket`;
- inbound `Process*`/event.

### Nếu thiếu exact data field

Resolve return object type của SharedData/Game API rồi enumerate metadata fields. Không scan toàn process trước.

### Nếu thiếu static table

Decrypt/extract `Config.unity3d` hoặc Interface bundle và commit **kết quả semantic** vào `database/`.

## Research ledgers

- `research/VERIFIED.md` — confirmed.
- `research/PROBABLE.md` — strong predictions.
- `research/HYPOTHESES.md` — ideas requiring validation.
- `research/TODO.md` — only remaining targeted work.

## Current state

Deep repository/client analysis has been recorded. Future work should be **targeted verification/implementation**, not a fresh general reverse-engineering pass.
