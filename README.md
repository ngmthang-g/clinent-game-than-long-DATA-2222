# Thần Long Client Research Database

Repo này chứa **frozen snapshot** của client Thần Long cùng knowledge base phục vụ phân tích/reverse-engineering.

## AI / developer: đọc ở đâu trước?

➡️ **Bắt đầu tại [`AI_INDEX.md`](./AI_INDEX.md)**.

Không phân tích lại toàn bộ binary nếu subsystem đã được mô tả trong `analysis/` hoặc `database/`.

## Knowledge base

- [`analysis/00_MASTER_RESEARCH_MAP.md`](./analysis/00_MASTER_RESEARCH_MAP.md) — kiến trúc tổng thể + phân loại file + ưu tiên reverse.
- [`analysis/01_IL2CPP_RUNTIME_METADATA.md`](./analysis/01_IL2CPP_RUNTIME_METADATA.md) — IL2CPP/metadata/runtime resolver.
- [`analysis/02_LUA_GAME_UI_NETWORK_API.md`](./analysis/02_LUA_GAME_UI_NETWORK_API.md) — Lua/Game/UI/Network API.
- [`analysis/03_WORLD_ENTITY_MAP_PATH.md`](./analysis/03_WORLD_ENTITY_MAP_PATH.md) — world/entity/NPC/map/pathfinding.
- [`analysis/04_INVENTORY_ITEMS_SHOP.md`](./analysis/04_INVENTORY_ITEMS_SHOP.md) — inventory/item/shop/auto sell.
- [`analysis/05_COMBAT_SKILLS_BUFFS.md`](./analysis/05_COMBAT_SKILLS_BUFFS.md) — combat/skills/buffs/auto fight.
- [`analysis/06_ASSETS_ENCRYPTION_BUNDLES.md`](./analysis/06_ASSETS_ENCRYPTION_BUNDLES.md) — asset bundles + FG decrypt.
- [`analysis/07_SUPPORT_MODULES_LAUNCHER.md`](./analysis/07_SUPPORT_MODULES_LAUNCHER.md) — Unity/support modules/launcher.
- [`analysis/08_FILE_BY_FILE_CATALOG.md`](./analysis/08_FILE_BY_FILE_CATALOG.md) — mô tả từng file/nhóm file trong snapshot, giá trị reverse và dự đoán nội dung.
- [`database/API_QUICK_REFERENCE.md`](./database/API_QUICK_REFERENCE.md) — tra nhanh class/method/API/RVA hints.
- [`database/NETWORK_COMMAND_CATALOG.md`](./database/NETWORK_COMMAND_CATALOG.md) — command/event vocabulary theo subsystem và cách diễn giải an toàn.

## Evidence state

- [`research/VERIFIED.md`](./research/VERIFIED.md) — fact đã xác nhận.
- [`research/PROBABLE.md`](./research/PROBABLE.md) — dự đoán có bằng chứng mạnh.
- [`research/HYPOTHESES.md`](./research/HYPOTHESES.md) — giả thuyết cần test.
- [`research/TODO.md`](./research/TODO.md) — chỉ còn targeted verification, không phải broad re-analysis.

## Binary note

Các binary lớn dùng Git LFS. GitHub API có thể hiển thị pointer text thay vì bytes thật. Documentation trong repo đã được xây từ original binary bytes của snapshot hiện tại.
