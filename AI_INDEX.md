# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## Mục tiêu

Repo này là **canonical knowledge base** cho client Thần Long hiện tại. Client được coi là snapshot cố định; mục tiêu là để AI sau **đọc tài liệu trước, không reverse lại toàn bộ binary từ đầu**.

## Bắt buộc đọc theo thứ tự

1. `AI_INDEX.md` — file này.
2. `analysis/00_MASTER_RESEARCH_MAP.md` — bản đồ kiến trúc + ưu tiên file.
3. `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md` — kết quả giải mã Config/Interface/Lua.
4. `research/VERIFIED.md` — các fact đã xác nhận.
5. Tài liệu subsystem/feature đúng với task.
6. `database/API_QUICK_REFERENCE.md`, `database/CONFIG_TABLE_CATALOG.md`, `database/PACKET_CATALOG.md` khi cần tra nhanh.
7. `research/PROBABLE.md` và `research/HYPOTHESES.md` khi cần hướng đào tiếp.

## Quy tắc cho mọi AI

### Không broad reverse lại nếu docs đã trả lời

Ví dụ:
- inventory/shop → `analysis/04_INVENTORY_ITEMS_SHOP.md` + `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`;
- Auto Train → `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` + `features/AUTO_TRAIN.md`;
- revive/Đầu thai → `features/AUTO_REVIVE.md`;
- Auto Sell → `features/AUTO_SELL.md`;
- NPC Trị liệu → `features/AUTO_HEAL_NPC.md`.

### Phân biệt độ chắc chắn

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — evidence mạnh, semantics chưa end-to-end verified.
- **HYPOTHESIS** — giả thuyết dùng để định hướng test.

Không được biến dự đoán thành fact.

### Repo là frozen snapshot

Chủ sở hữu không có kế hoạch thay client trong repo này. Không cần bắt user chạy hash/version check mỗi lần. Historic RVA chỉ để locate/debug; code cuối vẫn nên resolve semantic name khi có thể.

### LFS pointer không phải binary

GitHub Contents API có thể trả file LFS khoảng 130 byte. Deep analysis được làm trên original bytes của snapshot. Nếu cần disassembly mới, phải dùng original binary, không phân tích pointer text.

## Phase 2 — phát hiện làm thay đổi chiến lược reverse

`FGClientTool_Windows.dll` decrypt đã được tái tạo đủ để mở các bundle custom. Đã giải mã/extract:
- `Config.unity3d`
- `Interface.unity3d`
- `Translations.unity3d`
- `LoadingResources.unity3d`
- `Logo.unity3d`
- `Shared.unity3d`
- `Shared_2.unity3d`
- `data.unity3d` vốn đã UnityFS.

Kết quả:
- **75 Config XML TextAssets**;
- **338 UI layout XML TextAssets**;
- **339 Lua script classes** + global infrastructure scripts;
- **169 packet constants**;
- exact Lua payloads cho revive, sell, bag sort, item actions, GameDialog.

Vì vậy với UI/auto flow, thứ tự ưu tiên mới là:

`Lua source -> Config/Layout semantic data -> exact handler/payload -> native reverse only if still needed`.

## Bản đồ tài liệu

### Architecture / file priority
- `analysis/00_MASTER_RESEARCH_MAP.md`

### IL2CPP / metadata
- `analysis/01_IL2CPP_RUNTIME_METADATA.md`

### Lua / UI / network bridge
- `analysis/02_LUA_GAME_UI_NETWORK_API.md`

### World / entities / maps / pathfinding
- `analysis/03_WORLD_ENTITY_MAP_PATH.md`

### Inventory / items / shop
- `analysis/04_INVENTORY_ITEMS_SHOP.md`

### Combat / skills / buffs
- `analysis/05_COMBAT_SKILLS_BUFFS.md`

### Asset bundles / encryption
- `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md`

### Support modules / launcher
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md`

### File-by-file catalog
- `analysis/08_FILE_BY_FILE_CATALOG.md`

### Decrypted Config/Interface/Lua
- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`

### Built-in Auto Fight
- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`

### Exact actions/packets
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`

## Database quick lookup

- `database/API_QUICK_REFERENCE.md`
- `database/NETWORK_COMMAND_CATALOG.md`
- `database/CONFIG_TABLE_CATALOG.md`
- `database/PACKET_CATALOG.md`
- `database/PACKET_IDS.csv`
- `database/UI_LAYOUT_CALLBACKS.md`
- `database/LUA_SCRIPT_CATALOG.md`

## Feature specs

- `features/AUTO_TRAIN.md`
- `features/AUTO_SELL.md`
- `features/AUTO_REVIVE.md`
- `features/AUTO_HEAL_NPC.md`

## Entry points quan trọng

### World/runtime
- `LuaSystemSharedData.GetNearbySprites/GetNearbyObjects/GetLocalMapObjects/GetNearestNPC/GetNearByEnemies`
- `GScene`, `PathFinder`, `NodeGrid`

### Built-in auto/combat
- `AutoFight_Main:StartAutoFight`
- `Game.GetNearbySpritesWithPredicate`
- `Game.SelectTarget`
- `Game.ChaseTarget`
- `Game.RequestUsingSkillWithTarget/Pos`

### NPC/navigation
- `Game.GetNPCPosition`
- `Game.GoTo`
- `Game.GetNearestNPC`
- dynamic `GameDialog.Selections`

### Inventory/shop
- `GetFreeBagSpace`
- `GetItemsAtSite`
- `GetItemType/GetEquipType`
- `IsItemSellable/IsItemThrowable`
- `CMD_NPC_SHOP_SELL_REQUEST = 200036`

### UI/network
- `MainCallUI/CallUI/FindUI/HasScript/GetScript`
- `CMD_SHOW_GAMEDIALOG = 100007`
- `CMD_REVIVE_DATA = 200063`
- `CMD_BAG_SORT = 100006`

## Những việc không nên lặp lại

- CE scan HP từng offset khi query/entity API trả lời được.
- pixel/OCR cho item classification khi data API tồn tại.
- gọi `UIButton.HandleClickEvent` như static/global function.
- reuse UIButton pointer sau UI transition.
- fixed sleep làm state proof.
- gọi response handler như action request.
- hardcode RVA làm identity duy nhất.
- broad reverse LiveKit/baselib/D3D12 trước gameplay modules.
- bịa tọa độ NPC từ `AutoPath/NPCData`; dùng `Game.GetNPCPosition`.
- bịa `selectionID` cho Trị liệu; đọc active `GameDialog.Selections`.

## Current state

General deep reverse + asset/Lua Phase 2 đã được ghi lại. Future work nên là **targeted verification/implementation**, không phải một fresh general reverse-engineering pass.
