# Phase 2 — Decrypted Config, Interface, Lua and semantic databases

Status: **VERIFIED extraction for the frozen client snapshot**.

## 1. What changed from Phase 1

Phase 2 successfully crossed the asset boundary:
- reproduced `FGClientTool_Windows.dll` decryption behavior;
- restored `Config.unity3d`, `Interface.unity3d`, `Translations.unity3d`, `LoadingResources.unity3d`, `Logo.unity3d`, `Shared.unity3d`, `Shared_2.unity3d` to valid `UnityFS`;
- parsed `data.unity3d`, already UnityFS;
- decompressed UnityFS block/directory data;
- recovered Config XML, UI layout XML and embedded Lua source TextAssets.

This changes the preferred research route: many UI/automation questions can now be answered from readable game data and Lua rather than native disassembly.

## 2. Decryption model recovered

The game-specific DLL exports `FG_Decrypt` / `FG_Encrypt`.

Observed decrypt families:
1. legacy fixed head/tail transform around the first/last 128 bytes using key `0x0F`;
2. newer size-derived transform seeded by `file_size XOR 0x9E3779B9`, followed by 32-bit xorshift (`<<13`, `>>17`, `<<5`) to derive swap count and byte key.

A successful decode is identified by `UnityFS`, `UnityRaw` or `UnityWeb`.

Future AI should reuse this finding instead of re-disassembling `FGClientTool_Windows.dll` unless implementing a standalone extractor.

## 3. Restored bundle versions

| Bundle | Unity version | Role |
|---|---|---|
| `Config.unity3d` | `6000.3.7f1` | static gameplay/config tables |
| `Interface.unity3d` | `6000.3.7f1` | UI layouts + embedded Lua |
| `Translations.unity3d` | `6000.3.7f1` | translations |
| `LoadingResources.unity3d` | `6000.3.4f1` | loading resources |
| `Logo.unity3d` | `6000.3.4f1` | logo/branding resources |
| `Shared.unity3d` | `6000.3.4f1` | shared UI resources |
| `Shared_2.unity3d` | `6000.3.6f1` | shared UI resources |
| `data.unity3d` | `6000.3.6f1` | serialized player/resources data |

## 4. Config extraction

`Config.unity3d` yielded **75 valid named XML TextAssets**.

Verified high-value counts:
- NPCs: **1,003**
- Maps: **193**
- AutoPath records: **1,618** = 924 `NPCData` + 165 `Portal` + 506 `NPC` transitions + 23 `Item` destinations
- Items: **5,238**
- Equips: **22,763**
- Skills: **2,091**
- SkillProperties: **2,044**
- AutoSkills: **300**
- Magic attributes: **509**
- Monsters: **17,121**
- Factions: **17**
- FuBen scenarios: **19**

See `database/CONFIG_TABLE_CATALOG.md`.

## 5. NPC/map examples and coordinate correction

`NPCs` gives `ID`, `Name`, `ResName`, `Avarta`. `AutoPath/NPCData` links many NPC IDs to a MapID.

Examples:
- NPC `328` = **Ba Nhĩ**, `ResName=ALaBoNanRen2`, MapID `5`.
- NPC `373` = **Mã Kiêu Minh**, `ResName=ZhanDouXiaoYaoDiZi`, MapID `5`.
- Map `5` = **Lâu Lan**, `ResName=loulangucheng`, `Type=City`, `Level=75`.

Critical correction: `AutoPath/NPCData` does **not** contain NPC X/Y. Runtime Lua uses `Game.GetNPCPosition(npcID)` followed by `Game.GoTo`, which is stronger than hardcoded coordinates.

## 6. Interface extraction

`Interface.unity3d` yielded **338 XML layout TextAssets**. A handler scan found **1,469 explicit handler bindings** across click/select/hover/text/value/pointer events.

High-value layouts include `Revival_Layout`, `AutoFight_Layout`, `AutoTrainMonster_Layout`, `NPCShop_Layout`, `NPCShop_SellItemTab_Layout`, `RoleInfo_BagTab_Layout`, `MessageBox_Layout`, `GameDialog_Layout`, `AutoHp_Layout`, `Utilities_Layout`.

This is decisive evidence to locate UI actions by layout/script semantics instead of pixels or stale native UIButton pointers.

## 7. Lua source extraction

The interface bundle embeds readable Lua source. A semantic scan identifies **339 Lua script classes with colon-method definitions** plus global infrastructure such as `Global`, `Global_Constants`, `Global_Functions`, `Loader`, `Loader_Data`, `TCPPacketDefine`, `TCPCmdHandler`, `TCPCmdEventHandler`.

High-value scripts: `AutoFight_Main`, `AutoFight_FuBen`, `AutoTrainMonster`, `AutoHp`, `Utilities`, `Revival`, `NPCShop`, `NPCShop_SellItemTab`, `RoleInfo_BagTab`, `BagItemsGrid`, `GameDialog`, `MessageBox`.

## 8. Protocol definitions

`TCPPacketDefine` provides **169 symbolic packet IDs**. Exact packet existence is VERIFIED; exact payload is VERIFIED only where Lua constructs it.

Important IDs:
- `CMD_ITEM_ACTION = 100005`
- `CMD_BAG_SORT = 100006`
- `CMD_SHOW_GAMEDIALOG = 100007`
- `CMD_CLIENT_STALL = 100010`
- `CMD_NPC_SHOP_DATA = 200034`
- `CMD_NPC_SHOP_BUY_REQUEST = 200035`
- `CMD_NPC_SHOP_SELL_REQUEST = 200036`
- `CMD_REVIVE_DATA = 200063`

## 9. New priority order

For UI/automation flows:

`Lua source -> Config/Layout semantic data -> exact handler/payload -> native reverse only if still required`.

## 10. Remaining targeted unknown: healer selection

A healer NPC may present a server-built dynamic `GameDialog`. `GameDialog` receives `Selections[selectionID]=visibleText` and submits `selectionID:selectedItemID` via `CMD_SHOW_GAMEDIALOG`.

Therefore a fixed global “Trị liệu” selection ID is not currently proven. Correct approach: inspect the active `Selections`, match the treatment semantic label, use the actual selection ID and verify resulting state. This is a targeted runtime problem, not a reason to reverse the whole client again.
