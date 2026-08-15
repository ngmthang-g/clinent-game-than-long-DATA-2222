# Database navigation index

> Đây là lớp dữ liệu máy đọc/AI đọc được sinh từ Config/Interface/Lua đã giải mã. Khi một câu hỏi có thể trả lời từ database, **không broad reverse binary lại**.

## Static world/config

- `MAPS.csv` — 193 map records: MapID, Name, ResName, Level, Type, ServerID, Music.
- `npcs/NPCS_0001_0200.csv` … `NPCS_1001_1003.csv` — full 1,003 NPC rows với ID, Name, ResName, Avatar và AutoPath MapID/MapName khi có.
- `NPC_SERVICE_CANDIDATES.md` — phân loại heuristic healer/vendor/blacksmith/storage; verified data + clearly-labelled probable service inference.
- `FUBEN_SCENARIOS.csv` — 19 dungeon scenario definitions.
- `AUTOPATH_PORTAL_EDGES.csv` — 165 direct portal edges có From/To map + coordinates.
- `AUTOPATH_ITEM_DESTINATIONS.csv` — 23 static item/destination records.
- `autopath_npc/AUTOPATH_NPC_EDGES_0001_0170.csv` … `_0341_0506.csv` — 506 NPC-mediated/city travel edges.
- `CONFIG_TABLE_CATALOG.md` — schema/record-count catalog cho toàn bộ 75 Config TextAssets.

## Protocol/action

- `PACKET_IDS.csv` — full 169 `TCPPacketDefine` constants.
- `PACKET_CATALOG.md` — important packet meanings and verification rules.
- `NETWORK_COMMAND_CATALOG.md` — command/event vocabulary from earlier native/metadata research.
- `API_QUICK_REFERENCE.md` — high-value native/Lua bridge/API lookup.

## Lua/UI

- `LUA_SCRIPT_CATALOG.md` — semantic catalog of high-value Lua scripts among 339 classes.
- `UI_LAYOUT_CALLBACKS.md` — high-value UI layouts/callbacks from 338 layout files / 1,469 handler bindings.

## Data interpretation rules

1. `NPCs`/`AutoPath NPCData` provides NPC identity and map association, **not NPC X/Y**. Runtime `Game.GetNPCPosition(npcID)` is preferred.
2. `ResName` is useful for candidate classification but not automatically a service contract.
3. Static travel edges may have level/event/state restrictions; runtime `Game.GoTo` remains the preferred executor.
4. Packet name existence does not prove payload. Use exact payload only when Lua construction is documented in `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`.
5. For inventory, keep `ID` (instance) separate from `ItemID` (template) and `Position` (slot).

## Particularly useful frozen-snapshot fact

`NPC 339 = Đỗ Thanh Đằng`, `ResName=LangZhong1`, `MapID=5 = Lâu Lan`. This is a strong healer candidate. Exact “Trị liệu” dialog selection remains runtime/server-driven and must be selected from actual `GameDialog.Selections` rather than a guessed global numeric ID.
