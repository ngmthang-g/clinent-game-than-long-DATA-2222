# AI Knowledge Index — Thần Long frozen client snapshot

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`

## Mục tiêu

Repo này là **canonical knowledge base** cho client Thần Long snapshot cố định. AI sau phải đọc KB trước và chỉ reverse/trace đúng điểm còn thiếu, không mổ lại toàn bộ client.

## Bắt buộc đọc theo thứ tự

1. `AI_INDEX.md`
2. `analysis/00_MASTER_RESEARCH_MAP.md`
3. `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`
4. `research/VERIFIED.md` + `research/VERIFIED_PHASE2.md`
5. tài liệu subsystem/feature đúng task
6. `database/README.md` và database cụ thể
7. `research/PROBABLE.md` / `research/HYPOTHESES.md` / `research/TODO.md` nếu cần đào tiếp.

## Quy tắc cho mọi AI

### Không broad reverse lại nếu docs/database đã trả lời

- inventory/shop → `analysis/04_INVENTORY_ITEMS_SHOP.md` + `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
- UI/action lifecycle → `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` + `database/UI_PACKET_LIFECYCLE.md`
- nearby player/entity scanner → `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- Nga My/healing donor logic → `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`
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

Đã giải mã/đọc Config/Interface/Translations/shared bundles và `data.unity3d`.

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

The shipped UI itself proves structured runtime data routes and direct semantic actions.

### Nearby peaceful players

`MainUI_NearByPlayers_PlayersTab` calls `Game.GetNearByPeacePlayers(MaxPlayers)` and directly reads:

- RoleID
- Name
- Level
- FactionID
- HP
- MaxHP
- GuildName
- AvartaID
- TeamRank.

So nearby friendly HP/MaxHP/name/faction/guild scanning **does not require party membership, OCR or CE scanning**.

### Selected target

`Game.SelectedTarget` is consumed by `MainUI_OtherHeader` with RoleID, Type, Name, HPPercent, MPPercent, RagePercent, Level, FactionID and other type-specific state; target buffs are read with `Game.GetTargetBuffIcons(RoleID)`.

### Exact Auto menu action

`TopIcon:AutoTrainClick()` calls:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`

then updates display status. The visible `Đánh quái` settings tab is **not** the start command.

### Nga My donor engine

Exact frozen-client IDs:

- Phật Quang Phổ Chiếu = 406
- Thanh Tâm Phổ Thiện Chú = 424
- Kim Châm Độ Kiếp = 407
- Cải Tử Hoàn Sinh = 408.

Built-in code demonstrates `GetNearTeammates -> HP/MaxHP -> CastRange -> ChaseTarget -> RequestUsingSkillWithTarget`. `features/AUTO_BUFF.md` documents how to combine that verified donor action path with the verified peaceful-player scanner.

### UI packet lifecycle

Important state proofs are server/event-driven:

- `CMD_REVIVE_DATA` -> open/update/close `Revival` + `DeathActive()`
- `CMD_NPC_SHOP_DATA` -> open/refresh `NPCShop`
- `CMD_SHOW_GAMEDIALOG` -> replace/close/create `GameDialog`
- buff events -> Add/Update/Remove through `BuffFrame`.

See `database/UI_PACKET_LIFECYCLE.md`.

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
- `analysis/12_GLOBAL_LUA_HELPERS.md` — reusable helpers such as `GoToNPC`
- `analysis/13_UI_RUNTIME_ACTION_SURFACE.md` — deep UI event/action architecture
- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md` — exact nearby-player/target fields used by UI
- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md` — recovery/Nga My donor logic.

## Database map

Start at `database/README.md`.

### Static world data
- `database/MAPS.csv` — full 193 maps
- `database/npcs/NPCS_*.csv` — full 1,003 NPCs
- `database/NPC_SERVICE_CANDIDATES.md`
- `database/FUBEN_SCENARIOS.csv`
- `database/AUTOPATH_PORTAL_EDGES.csv`
- `database/AUTOPATH_ITEM_DESTINATIONS.csv`
- `database/autopath_npc/AUTOPATH_NPC_EDGES_*.csv`
- `database/CONFIG_TABLE_CATALOG.md`.

### Protocol/API/UI
- `database/API_QUICK_REFERENCE.md`
- `database/NETWORK_COMMAND_CATALOG.md`
- `database/PACKET_CATALOG.md`
- `database/PACKET_IDS.csv`
- `database/UI_LAYOUT_CALLBACKS.md`
- `database/LUA_SCRIPT_CATALOG.md`
- `database/UI_PACKET_LIFECYCLE.md`
- `database/AUTO_SETTINGS_SCHEMA.md`.

## Feature specs

- `features/AUTO_TRAIN.md`
- `features/AUTO_BUFF.md`
- `features/AUTO_SELL.md`
- `features/AUTO_REVIVE.md`
- `features/AUTO_HEAL_NPC.md`.

## High-value exact facts

### Lâu Lan healer candidate

**NPC `339` = Đỗ Thanh Đằng, `ResName=LangZhong1`, Map `5` = Lâu Lan.** Static identity/map is VERIFIED. Healer service is a strong semantic inference; exact “Trị liệu” selection must still be read from actual `GameDialog.Selections`.

### NPC navigation

Built-in helper `GoToNPC(mapID,npcID)` uses `Game.GetNPCPosition -> Game.GoTo -> Game.ClickNPC`. Do not invent NPC X/Y from AutoPath NPCData.

### Auto Train

`C_AutoModel.Train = 1`; semantic start is `AutoFight_Main:StartAutoFight(C_AutoModel.Train)` or shipped wrapper `TopIcon:AutoTrainClick()`.

### Auto Sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`, payload `itemInstanceID:NpcShopID:ShopID`.

### Đầu thai/revive

`CMD_REVIVE_DATA = 200063`: normal/Đầu thai=1, newbie=2, skill revive=3.

### Dynamic NPC dialog

`Selections[selectionID] = visibleText`; submit through `CMD_SHOW_GAMEDIALOG=100007` payload `selectionID:SelectedItemID`.

## Những việc không nên lặp lại

- CE scan từng HP offset khi structured nearby-player/game data API đủ dùng.
- pixel/OCR item/player data khi semantic fields tồn tại.
- click visible `Đánh quái` tab để cố khởi động Train.
- gọi `UIButton.HandleClickEvent` như static/global function.
- reuse UIButton pointer sau UI transition.
- dùng fixed sleep làm state proof.
- gọi response handler như action request.
- hardcode RVA làm identity duy nhất.
- broad reverse LiveKit/baselib/D3D12 trước gameplay modules.
- bịa NPC X/Y thay vì `Game.GetNPCPosition`.
- bịa fixed `selectionID` cho Trị liệu.

## Current state

General reverse + decrypted asset/Lua + deep UI/runtime semantic analysis đã được ghi lại. Future work phải là **targeted runtime verification/implementation** cho những state động còn thiếu, không phải fresh general reverse-engineering pass.
