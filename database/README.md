# Database navigation index

> Machine/AI-readable data derived from the frozen client's decrypted Config/Interface/Lua plus verified runtime/native evidence. If the database already answers a question, **do not broad-reverse the binaries again**.

---

## Fast lookup entrypoints

Use the smallest entrypoint that matches the question:

- `SUBSYSTEM_SOURCE_MAP.md` — **best first file when asking “where should I look for this subsystem?”** Maps runtime API vs Lua/UI vs Config vs packet evidence.
- `FACTS_README.md` — how to use atomic facts.
- `FACTS.jsonl` — high-value exact IDs/constants/contracts/counts.
- `FINDING_TO_DOC_MAP.md` — finding/question -> canonical detailed document.
- `SEMANTIC_JOIN_MAP.md` — how runtime IDs and Config tables connect; includes VERIFIED joins and clearly-labelled join candidates.

For implementation tasks, use `AI_BOOTSTRAP.md -> AI_ROUTER.md` first, then come here only for the needed records.

---

## Config / static semantic navigation

- `CONFIG_TABLE_CATALOG.md` — exact 75 Config TextAsset table names, row counts and high-level fields.
- `static/README.md` — query-oriented storage plan for large normalized Config datasets.
- `static/LOOKUP_GUIDE.md` — index -> chunk strategy to prevent AI context overload.
- `SEMANTIC_JOIN_MAP.md` — cross-table/runtime relationship map.

Canonical analysis:

- `analysis/28_STATIC_DATA_DATABASE_EXPANSION.md` — detailed Items/Skills/Magic/Monsters/Equips schemas.
- `analysis/32_CONFIG_DOMAIN_ATLAS.md` — all 75 tables grouped by gameplay domain/value.
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md` — next high-value normalization targets and preservation rules.

### High-value verified source sizes

Combat/skills:

- Skills 2,091
- SkillProperties 2,044
- AutoSkills 300
- MagicAtrributes 509
- Factions 17
- Books 128.

Inventory/equipment:

- Items 5,238
- Equips 22,763
- Medicines 692
- Gems 1,154.

World/task:

- Monsters 17,121
- Tasks 516
- GrowPoints 407
- GuildTask 360.

Pet/Spirit:

- Pets 8,349
- Spirits 1,889.

These are **lookup datasets**, not mandatory context.

---

## World / map / NPC / routes

Already materialized databases:

- `MAPS.csv` — 193 map records.
- `npcs/NPCS_0001_0200.csv` … `NPCS_1001_1003.csv` — all 1,003 NPC rows with identity and AutoPath map association where available.
- `NPC_SERVICE_CANDIDATES.md` — doctor/vendor/blacksmith/storage candidate families; service inference remains clearly labelled until runtime proof.
- `FUBEN_SCENARIOS.csv` — 19 dungeon/scenario definitions.
- `AUTOPATH_PORTAL_EDGES.csv` — 165 direct portal edges.
- `AUTOPATH_ITEM_DESTINATIONS.csv` — 23 item/destination records.
- `autopath_npc/AUTOPATH_NPC_EDGES_*.csv` — 506 NPC-mediated transitions.

Important rules:

- NPC static data/map association does **not** provide the normal live NPC X/Y; use `Game.GetNPCPosition(npcID)`.
- static route edges may have level/quest/event restrictions; runtime `Game.GoTo` is still the preferred executor.
- `ResName` may classify a service **candidate**, not prove a service contract.

---

## Protocol / exact action lookup

- `PACKET_IDS.csv` — all 169 exact `TCPPacketDefine` constants.
- `PACKET_CATALOG.md` — important IDs and safety rules.
- `NETWORK_COMMAND_CATALOG.md` — protocol vocabulary plus current evidence levels: symbol -> exact ID -> exact request -> request/response lifecycle.
- `API_QUICK_REFERENCE.md` — high-value runtime/Game/Lua/native API lookup.

Exact frozen examples already solved:

- Sell: `CMD_NPC_SHOP_SELL_REQUEST=200036`, payload `itemInstanceID:NpcShopID:ShopID`.
- GameDialog: `CMD_SHOW_GAMEDIALOG=100007`, payload `selectionID:SelectedItemID`.
- Revive: `CMD_REVIVE_DATA=200063`, normal/Đầu thai=1, newbie=2, skill=3.
- Item action: `CMD_ITEM_ACTION=100005` with observed Equip/Use/Abandon/Move/Split action formats.
- Bag sort: `CMD_BAG_SORT=100006`.

Packet name/ID alone does not prove payload. Use only legitimate Lua/native construction as exact request evidence.

---

## Lua / UI

- `LUA_SCRIPT_CATALOG.md` — high-value script catalog among 339 Lua classes.
- `UI_LAYOUT_CALLBACKS.md` — callback/layout catalog from 338 layouts and 1,469 bindings.
- `UI_PACKET_LIFECYCLE.md` — packet/event -> UI/state lifecycle.
- `AUTO_SETTINGS_SCHEMA.md` — built-in Auto settings.
- `NGAMY_SUPPORT_SKILLS.md` — corrected Nga My support skill identities.

For a visible button/menu question, preferred search order:

```text
<Panel>_Layout
 -> same-name Lua script
 -> actual Game/GUI/Network call
 -> server/runtime result
```

Do not start with mouse coordinates or a stale UIButton pointer.

---

## Static-to-runtime relationship shortcuts

See `SEMANTIC_JOIN_MAP.md` for detail.

Important roots:

```text
live item.ItemID -> Items / Equips
runtime SkillID -> Skills -> SkillProperties -> MagicAtrributes
NPCID -> NPCs -> AutoPath MapID -> runtime GetNPCPosition
MapID -> Maps + AutoPath route graph
Task type/parameters -> NPC/Monster/Item/GrowPoint/Map (type-specific)
runtime Pet/Spirit identity -> Pets/Spirits template data
```

Do not assume identical numeric values are joins without semantic evidence.

---

## Data interpretation rules

1. Static template data describes **what something is**; runtime/server state describes **what exists/is true now**.
2. Live inventory: `ID` instance != `ItemID` template != `Position` slot != `Site` container.
3. `Equips.EquipPoint == 0` is the static Weapon slot identity; `Type < 10` is not a universal weapon test.
4. `Game.GetNearByPeacePlayers(limit)` already exposes nearby non-party RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank.
5. `Game.GetBuffs()` already exposes BuffID/DurationTick/Stack.
6. `FACTS.jsonl` is a retrieval index; its `source` document remains canonical for evidence/context.
7. Unknown Config fields should be preserved during normalization instead of discarded.
8. Response handlers are not request actions.
9. Fixed delays are not success proof.

---

## Particularly useful frozen-snapshot facts

- Map 5 = Lâu Lan.
- NPC 339 = Đỗ Thanh Đằng, `ResName=LangZhong1`, Map 5; strong healer candidate.
- Exact “Trị liệu” selection remains active server `GameDialog.Selections`, not a fixed global numeric ID.
- Skill 407 = Xung Hư Dưỡng Khí; actual Kim Châm Độ Kiếp = 423.
- Built-in Train start = `GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)` with Train=1.
- Static Weapon = `EquipPoint==0`.

---

## Current database expansion priority

Main next data work is defined in `research/TODO.md`:

```text
Skills/SkillProperties/AutoSkills/Factions/Books
 -> Items/Equips/Medicines
 -> Tasks/GrowPoints
 -> Pets/Spirits
```

Full large row chunks are not currently present under `database/static/`; do not pretend they exist until they are actually committed.
