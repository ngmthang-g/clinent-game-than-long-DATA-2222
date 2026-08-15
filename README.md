# Thần Long Client Research Database

Repo này chứa **frozen snapshot** của client Thần Long cùng knowledge base phục vụ phân tích/reverse-engineering và build tool.

## AI / developer: đọc ở đâu trước?

➡️ **Bắt đầu tại [`AI_BOOTSTRAP.md`](./AI_BOOTSTRAP.md)**.

Sau đó đọc [`AI_ROUTER.md`](./AI_ROUTER.md) để chọn đúng `contexts/BUILD_*.md` cho task hiện tại.

**Không đọc toàn bộ repo trước khi làm việc.** Repo này được thiết kế như thư viện tra cứu nhiều tầng để AI không bị ngợp context khi knowledge base tiếp tục lớn lên.

Deep repository map nằm tại [`AI_INDEX.md`](./AI_INDEX.md).

## Routing layer

- [`AI_BOOTSTRAP.md`](./AI_BOOTSTRAP.md) — kiến trúc + fact guardrails ngắn gọn.
- [`AI_ROUTER.md`](./AI_ROUTER.md) — task → context pack.
- [`contexts/`](./contexts/) — context pack theo từng subsystem/build task.
- [`database/FACTS.jsonl`](./database/FACTS.jsonl) — atomic high-value facts để tra nhanh.
- [`database/FINDING_TO_DOC_MAP.md`](./database/FINDING_TO_DOC_MAP.md) — finding → canonical document.
- [`KB_METHOD.md`](./KB_METHOD.md) — quy tắc bảo toàn kiến thức/evidence.

## Deep knowledge base

- [`analysis/00_MASTER_RESEARCH_MAP.md`](./analysis/00_MASTER_RESEARCH_MAP.md) — kiến trúc tổng thể + phân loại file + ưu tiên reverse.
- [`analysis/01_IL2CPP_RUNTIME_METADATA.md`](./analysis/01_IL2CPP_RUNTIME_METADATA.md) — IL2CPP/metadata/runtime resolver.
- [`analysis/02_LUA_GAME_UI_NETWORK_API.md`](./analysis/02_LUA_GAME_UI_NETWORK_API.md) — Lua/Game/UI/Network API.
- [`analysis/03_WORLD_ENTITY_MAP_PATH.md`](./analysis/03_WORLD_ENTITY_MAP_PATH.md) — world/entity/NPC/map/pathfinding.
- [`analysis/04_INVENTORY_ITEMS_SHOP.md`](./analysis/04_INVENTORY_ITEMS_SHOP.md) — inventory/item/shop.
- [`analysis/05_COMBAT_SKILLS_BUFFS.md`](./analysis/05_COMBAT_SKILLS_BUFFS.md) — combat/skills/buffs.
- [`analysis/06_ASSETS_ENCRYPTION_BUNDLES.md`](./analysis/06_ASSETS_ENCRYPTION_BUNDLES.md) — asset bundles + FG decrypt.
- [`analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`](./analysis/09_PHASE2_DECRYPTED_DATA_LUA.md) — decrypted Config/Interface/Lua breakthrough.
- [`analysis/21_MAIN_THREAD_DISPATCHER.md`](./analysis/21_MAIN_THREAD_DISPATCHER.md) — exact game-owned MainThread queue/Update/Action.Invoke chain.
- [`analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`](./analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md) — game-owned System.Action producer pattern.

## Database

Start at [`database/README.md`](./database/README.md).

Large static datasets are **lookup sources**, not files AI should preload completely.

## Evidence state

- [`research/VERIFIED.md`](./research/VERIFIED.md)
- [`research/VERIFIED_PHASE2.md`](./research/VERIFIED_PHASE2.md)
- [`research/VERIFIED_PHASE3.md`](./research/VERIFIED_PHASE3.md)
- [`research/PROBABLE.md`](./research/PROBABLE.md)
- [`research/HYPOTHESES.md`](./research/HYPOTHESES.md)
- [`research/TODO.md`](./research/TODO.md)

## Binary note

Các binary lớn dùng Git LFS. GitHub API có thể hiển thị pointer text thay vì bytes thật. Documentation trong repo đã được xây từ original binary bytes của snapshot hiện tại.
