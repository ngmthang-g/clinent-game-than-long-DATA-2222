# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## Mục tiêu

Repo này là **canonical knowledge base** cho client Thần Long snapshot cố định. AI sau phải đọc KB trước và chỉ reverse/trace đúng điểm còn thiếu, không mổ lại toàn bộ client.

## Bắt buộc đọc theo thứ tự

1. `AI_INDEX.md`
2. `analysis/00_MASTER_RESEARCH_MAP.md`
3. `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`
4. `research/VERIFIED.md` + `research/VERIFIED_PHASE2.md` + `research/VERIFIED_PHASE3.md`
5. tài liệu subsystem/feature đúng task
6. `database/README.md` và database cụ thể
7. `research/PROBABLE.md` / `research/HYPOTHESES.md` / `research/TODO.md` nếu cần đào tiếp.

## Quy tắc cho mọi AI

### Không broad reverse lại nếu docs/database đã trả lời

- inventory/shop → `analysis/04_INVENTORY_ITEMS_SHOP.md` + `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- exact packets/actions → `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
- UI/action lifecycle → `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` + `database/UI_PACKET_LIFECYCLE.md`
- nearby player/entity scanner → `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- player/social target object → `analysis/16_PLAYER_INTERACTION_UI_API.md`
- Nga My/healing donor → `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` + `database/NGAMY_SUPPORT_SKILLS.md`
- buff IDs/duration/stack → `analysis/17_BUFF_RUNTIME_SCHEMA.md`
- skill cooldown/quick skills/F1 semantics → `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- progress/Captcha safety → `analysis/19_PROGRESS_CAPTCHA_SAFETY.md`
- main-thread execution → `analysis/21_MAIN_THREAD_DISPATCHER.md`
- map readiness/object navigation → `analysis/22_MAP_MINIMAP_RUNTIME.md`
- Auto Train → `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` + `features/AUTO_TRAIN.md`
- Auto Buff → `features/AUTO_BUFF.md`
- revive/Đầu thai → `features/AUTO_REVIVE.md`
- Auto Sell → `features/AUTO_SELL.md`
- NPC Trị liệu → `features/AUTO_HEAL_NPC.md` + `database/NPC_SERVICE_CANDIDATES.md`
- NPC/map/route → `database/README.md`, `database/npcs/`, `MAPS.csv`, AutoPath databases.

### Mức chắc chắn

- **VERIFIED** — direct binary/metadata/decrypted asset/Lua/runtime evidence.
- **PROBABLE** — evidence mạnh nhưng chưa end-to-end/runtime-confirmed.
- **HYPOTHESIS** — hướng test, không phải fact.

### Frozen snapshot

Chủ sở hữu không có kế hoạch thay client trong repo. Không cần bắt user hash-check mỗi lần. Historic RVA chỉ để locate/debug; semantic name/ID ưu tiên hơn hardcode address.

### Git LFS

Contents API có thể trả `.dll/.exe/.dat` dưới dạng pointer ~130 byte. Deep analysis đã dùng original bytes. Nếu cần disassembly mới, phải dùng original LFS/local bytes, không phân tích pointer text.

## Phase 2 — decrypted semantic data breakthrough

Đã tái tạo đủ `FGClientTool_Windows.dll` decrypt để mở custom bundles và extract semantic data.

Kết quả chính:
- **75 Config XML TextAssets**
- **338 UI layout XML TextAssets**
- **1,469 UI handler bindings**
- **339 high-level Lua script classes** + global infrastructure
- **169 TCP packet constants**
- exact Lua payloads cho revive, sell, bag sort, item actions, GameDialog.

Với UI/automation, ưu tiên:

`Lua source -> Config/Layout semantic data -> exact handler/payload -> native reverse only if still needed`.

## Phase 3 — UI/runtime breakthrough

### Nearby peaceful players

`Game.GetNearByPeacePlayers(MaxPlayers)` feeds shipped UI fields RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID and TeamRank. Nearby friendly scanning therefore does not require party membership, OCR or CE value search.

### Selected target / other-player object

`Game.SelectedTarget` exposes target identity/vitals/type data. `OtherRolePopup` additionally consumes TeamID, GroupID, GuildID, GuildRank and AlliesID and uses RoleID-driven actions.

### Exact Auto menu action

`TopIcon:AutoTrainClick()` calls `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`. Visible `Đánh quái` in settings is not the start command.

### Nga My donor — corrected identity

Actual Config IDs:

- 406 Phật Quang Phổ Chiếu
- **407 Xung Hư Dưỡng Khí**
- 408 Khởi Tử Hồi Sinh
- **423 Kim Châm Độ Kiếp**
- 424 Thanh Tâm Phổ Thiện Chú.

Legacy Lua key `KIMCHAMDOKIEP` points to 407 but visible UI + Config prove 407 is Xung Hư Dưỡng Khí. Never copy that misleading name into new code. Built-in AutoHp fallback is 406 -> 424 -> 407.

### Skill cooldown / F-key semantics

`Game.GetSkillCooldown(skillID)` returns passed/cooldown ticks. SkillBar semantic action is `Game.UseSkill(skillID)`; physical F-key position is only presentation/configuration.

### Buff runtime

Local `Game.GetBuffs()` exposes BuffID, DurationTick(ms), Stack; GetBuffData/GetBuffProperties add semantic information; Add/Update/Remove events provide state proof.

### Bag/shop runtime

Bag UI renders `Game.GetItemsAtSite(Site)` and receives AddItem/RemoveItem/UpdateItemsList events. NPC Shop uses current item instance ID + current NpcShopID/ShopID; Quick Sell is only a UI wrapper around the same request.

### Map runtime

`Game.IsMapReady`, `GetLocalMapObjects`, `GetNearbyObjects`, `GetCurrentMoveDestination`, `MoveTo` and `GoTo` provide real map/movement state. Use them instead of fixed post-map delays.

### Main-thread bridge candidate

`FGStudio.Engine.Utilities.MainThread` exposes singleton Instance, Execute(Action), Update, DoExecuteWorks and `ConcurrentQueue<Action> waitToBeProcess`. Surface is verified; exact enqueue/drain execution needs final targeted proof before mutable external actions.

### Captcha safety

`NewCaptcha` opens a user-verification UI. Automation must pause and require manual user handling; no auto-solving/bypass.

## Analysis map

- `analysis/00_MASTER_RESEARCH_MAP.md` — architecture/file priority
- `analysis/01_IL2CPP_RUNTIME_METADATA.md` — IL2CPP/metadata
- `analysis/02_LUA_GAME_UI_NETWORK_API.md` — Lua bridge/UI/network
- `analysis/03_WORLD_ENTITY_MAP_PATH.md` — world/entity/map/path
- `analysis/04_INVENTORY_ITEMS_SHOP.md` — inventory/shop
- `analysis/05_COMBAT_SKILLS_BUFFS.md` — combat/skills/buffs
- `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` — asset encryption
- `analysis/07_SUPPORT_MODULES_LAUNCHER.md` — support/launcher
- `analysis/08_FILE_BY_FILE_CATALOG.md` — file-by-file catalog
- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md` — decrypted Config/Interface/Lua
- `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md` — built-in train/PK/quest/FuBen engine
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md` — exact packet/action payloads
- `analysis/12_GLOBAL_LUA_HELPERS.md` — helpers such as GoToNPC
- `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` — UI event/action architecture
- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` — nearby-player/target schema
- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` — recovery/Nga My donor + corrected skill naming
- `analysis/16_PLAYER_INTERACTION_UI_API.md` — selected-player/social data/actions
- `analysis/17_BUFF_RUNTIME_SCHEMA.md` — BuffID/duration/stack/properties/events
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md` — quick skills/cooldown/semantic use
- `analysis/19_PROGRESS_CAPTCHA_SAFETY.md` — progress + Captcha guard
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md` — bag/events/shop/quick-sell internals
- `analysis/21_MAIN_THREAD_DISPATCHER.md` — game-owned MainThread dispatcher target
- `analysis/22_MAP_MINIMAP_RUNTIME.md` — map readiness/local objects/movement/world map.

## Database map

Start at `database/README.md`.

Static world data includes full maps/NPCs/FuBen/AutoPath databases. Protocol/API/UI references include packet IDs, API quick reference, UI callbacks, Lua catalog, UI lifecycle, AutoSettings and `database/NGAMY_SUPPORT_SKILLS.md`.

## Feature specs

- `features/AUTO_TRAIN.md`
- `features/AUTO_BUFF.md`
- `features/AUTO_SELL.md`
- `features/AUTO_REVIVE.md`
- `features/AUTO_HEAL_NPC.md`.

## High-value exact facts

- NPC 339 = Đỗ Thanh Đằng, ResName LangZhong1, Map 5 Lâu Lan; exact treatment selection remains runtime GameDialog data.
- `GoToNPC` uses GetNPCPosition -> GoTo -> ClickNPC.
- Train start = `StartAutoFight(C_AutoModel.Train)`.
- Sell = packet 200036, payload `itemInstanceID:NpcShopID:ShopID`.
- Revive = packet 200063; normal/Đầu thai=1, newbie=2, skill=3.
- GameDialog selection submit = packet 100007, `selectionID:SelectedItemID`.

## Những việc không nên lặp lại

- CE scan individual HP offsets when semantic APIs already expose needed data.
- pixel/OCR item/player classification when semantic fields exist.
- click visible Đánh quái settings tab as Train start.
- use stale UIButton instances across transitions.
- fixed sleep as state proof.
- call response handlers as request actions.
- hardcode RVA as sole identity.
- invent NPC X/Y when GetNPCPosition exists.
- invent treatment selection IDs.
- trust misleading internal variable names without Config/UI cross-check.

## Current state

General reverse + decrypted asset/Lua + deep UI/runtime semantic analysis are recorded. Remaining work should be targeted runtime verification/implementation, especially the main-thread dispatcher and server-dynamic interactions, not a new broad reverse pass.
