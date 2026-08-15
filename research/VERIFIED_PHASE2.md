# VERIFIED Phase 2 — decrypted assets, Lua semantics and static databases

> Đây là các fact được bổ sung sau Phase 1. Nguồn bằng chứng gồm original client bytes, decrypted UnityFS bundles, XML TextAssets và Lua source được trích trực tiếp từ snapshot cố định.

## 1. Custom bundles đã được giải mã thành UnityFS

Status: **VERIFIED**

Đã khôi phục và đọc được:
- `Config.unity3d` → Unity `6000.3.7f1`
- `Interface.unity3d` → Unity `6000.3.7f1`
- `Translations.unity3d` → Unity `6000.3.7f1`
- `LoadingResources.unity3d` → Unity `6000.3.4f1`
- `Logo.unity3d` → Unity `6000.3.4f1`
- `Shared.unity3d` → Unity `6000.3.4f1`
- `Shared_2.unity3d` → Unity `6000.3.6f1`
- `data.unity3d` vốn đã là UnityFS `6000.3.6f1`.

## 2. Cơ chế decrypt của FGClientTool đã được hiểu đủ để tái tạo

Status: **VERIFIED bằng native analysis + successful decode**

`FGClientTool_Windows.dll` có `FG_Decrypt/FG_Encrypt`. Decrypt xử lý ít nhất hai family:
- legacy head/tail transform dùng key `0x0F`;
- size-derived transform dùng seed `file_size XOR 0x9E3779B9`, sau đó xorshift 32-bit (`<<13`, `>>17`, `<<5`) để sinh tham số swap/byte transform.

Kết quả hợp lệ được nhận biết bởi `UnityFS`, `UnityRaw`, `UnityWeb`.

## 3. Config bundle chứa 75 bảng XML semantic

Status: **VERIFIED**

Đã extract 75 named XML TextAssets. Các bảng nổi bật và số record:
- NPCs: 1,003
- Maps: 193
- AutoPath: 1,618
- Items: 5,238
- Equips: 22,763
- Skills: 2,091
- SkillProperties: 2,044
- AutoSkills: 300
- MagicAtrributes: 509
- Monsters: 17,121
- Factions: 17
- FuBenScenarios: 19
- Pets: 8,349
- Tasks: 516
- Gems: 1,154
- Medicines: 692.

Full catalog: `database/CONFIG_TABLE_CATALOG.md`.

## 4. NPC database và map database đã được trích trực tiếp

Status: **VERIFIED**

`NPCs.xml` chứa `ID`, `Name`, `ResName`, `Avarta`. `AutoPath/NPCData` liên kết nhiều NPC với `MapID`.

Ví dụ verified:
- `328` = Ba Nhĩ, Map 5 Lâu Lan.
- `337` = Đỗ Bất Đằng, `LangZhong1`, Map 5 Lâu Lan.
- `338` = Đỗ Hoàng Đằng, `LangZhong1`, Map 5 Lâu Lan.
- **`339` = Đỗ Thanh Đằng, `LangZhong1`, Map 5 Lâu Lan.**
- `373` = Mã Kiêu Minh, Map 5 Lâu Lan.
- `912` = Tháp trị liệu, `ZhiLiaoTa`; static AutoPath mapping không có trong bảng hiện tại.
- Map `5` = Lâu Lan, `loulangucheng`, City, level 75.

Full NPC rows nằm ở `database/npcs/`; maps nằm ở `database/MAPS.csv`.

## 5. Không có X/Y NPC trong `AutoPath/NPCData`

Status: **VERIFIED**

`NPCData` chỉ có semantic NPC ID/MapID/Name. Không được gán X/Y tưởng tượng từ bảng này.

Lua built-in dùng `Game.GetNPCPosition(npcID)` để lấy vị trí runtime rồi `Game.GoTo(...)`.

## 6. Static portal graph được extract

Status: **VERIFIED**

`AutoPath.xml` có 165 `Portal` edges với FromMapID/X/Y và ToMapID/X/Y. Database: `database/AUTOPATH_PORTAL_EDGES.csv`.

Ngoài ra có 23 `Item` destination entries: `database/AUTOPATH_ITEM_DESTINATIONS.csv`.

Static graph hữu ích cho route planning, nhưng điều kiện runtime/portal availability vẫn có thể cần kiểm tra.

## 7. FuBen scenario database có 19 definitions

Status: **VERIFIED**

`FuBenScenarios.xml` cung cấp dungeon map, gather map/NPC/X/Y, min players, min level, timeout và card-month requirement. Database: `database/FUBEN_SCENARIOS.csv`.

## 8. Interface bundle chứa 338 layout XML và 1,469 handler bindings

Status: **VERIFIED**

Các layout quan trọng:
- `Revival_Layout`
- `AutoFight_Layout`
- `AutoTrainMonster_Layout`
- `AutoHp_Layout`
- `Utilities_Layout`
- `NPCShop_Layout`
- `NPCShop_SellItemTab_Layout`
- `RoleInfo_BagTab_Layout`
- `MessageBox_Layout`
- `GameDialog_Layout`.

Semantic callback catalog: `database/UI_LAYOUT_CALLBACKS.md`.

## 9. Interface bundle chứa readable Lua source

Status: **VERIFIED**

Đã nhận diện 339 Lua classes có colon-methods cùng global infrastructure như:
- `Global`, `Global_Constants`, `Global_Functions`
- `Loader`, `Loader_Data`
- `TCPPacketDefine`
- `TCPCmdHandler`
- `TCPCmdEventHandler`.

High-value scripts: `AutoFight_Main`, `AutoFight_FuBen`, `AutoTrainMonster`, `AutoHp`, `Utilities`, `Revival`, `NPCShop`, `NPCShop_SellItemTab`, `RoleInfo_BagTab`, `BagItemsGrid`, `GameDialog`, `MessageBox`.

## 10. TCPPacketDefine có 169 exact symbolic packet IDs

Status: **VERIFIED**

Full list: `database/PACKET_IDS.csv`.

Important constants:
- `CMD_ITEM_ACTION = 100005`
- `CMD_BAG_SORT = 100006`
- `CMD_SHOW_GAMEDIALOG = 100007`
- `CMD_CLIENT_STALL = 100010`
- `CMD_NPC_SHOP_DATA = 200034`
- `CMD_NPC_SHOP_BUY_REQUEST = 200035`
- `CMD_NPC_SHOP_SELL_REQUEST = 200036`
- `CMD_REVIVE_DATA = 200063`.

## 11. Exact revive/Đầu thai action đã được giải quyết

Status: **VERIFIED từ Lua source**

`C_RevivalType`:
- Normal = 1
- NewbieRevival = 2
- SkillRevival = 3.

`Revival` handlers:
- Tân thủ → `ButtonNewbieReviveClicked` → payload `"2"`
- Hồi sinh → `ButtonSkillReviveClicked` → payload `"3"`
- Đầu thai → `ButtonGoToInfernalClicked` → payload `"1"`

Packet: `CMD_REVIVE_DATA = 200063`.

## 12. Exact NPC shop sell request đã được giải quyết

Status: **VERIFIED từ `NPCShop_SellItemTab`**

Packet: `CMD_NPC_SHOP_SELL_REQUEST = 200036`.

Payload:

`itemInstanceID:NpcShopID:ShopID`

Trong đó `dbItemData.ID` là **instance/database ID**, không phải template `ItemID`.

Original Lua còn:
- chặn quest ItemID range `40000000..49999999`;
- kiểm tra `Game.IsItemSellable(ItemID)`.

## 13. Exact bag sort và một số item actions đã được giải quyết

Status: **VERIFIED**

Bag sort:
- packet `CMD_BAG_SORT = 100006`
- bag site `C_ItemSite.Bag = 10`
- payload `"10"`.

`CMD_ITEM_ACTION = 100005` examples:
- Equip → `1:instanceID`
- Use → `3:instanceID`
- Abandon → `4:instanceID`
- Split → `8:instanceID:quantity`.

## 14. Dynamic `GameDialog` semantics đã được giải quyết

Status: **VERIFIED**

Server/client dialog data có `Selections[selectionID] = visibleText`. UI clone button và lưu selection ID vào `Tag`.

Click action gửi:

`CMD_SHOW_GAMEDIALOG = 100007`

Payload:

`selectionID:SelectedItemID`

Default SelectedItemID là `-1` nếu không chọn award item.

## 15. Built-in Auto Fight là engine semantic thật

Status: **VERIFIED từ Lua source**

`C_AutoModel`:
- None=0
- Train=1
- PK=2
- Quest=3
- AutoPath=4
- Fllow=5
- FuBen=6.

`AutoFight_Main:StartAutoFight(C_AutoModel.Train)` là semantic entry cho train mode. “Đánh quái” trong UI là tab cấu hình, không phải bản thân combat engine.

Engine dùng:
- `Game.GetNearbySpritesWithPredicate`
- `Game.HasPath`
- `Game.SelectTarget`
- `Game.ChaseTarget`
- `Game.RequestUsingSkillWithTarget/Pos`
- `Game.ReloadTarget`
- `Game.IsSelectTargetDie`
- `Game.GetCurrentHP`.

## 16. Built-in Auto Fight có internal NPC route flow

Status: **VERIFIED**

`GoToNPC(mapID,npcID)`:
1. chuyển map bằng `Game.GoTo(mapID,-1,-1,callback)` nếu cần;
2. lấy `Game.GetNPCPosition(npcID)`;
3. đi tới vị trí bằng `Game.GoTo(mapID,X,Y,callback)`;
4. lấy `Game.GetNearestNPC(npcID)`;
5. interact/select nearest NPC bằng internal Game API khi state phù hợp.

## 17. Built-in Auto Fight có loot/bag-space semantic logic

Status: **VERIFIED**

Loot flow dùng `Game.GetNearbyItemPack`, `Game.HasPath`, `Game.MoveToEx`, `Game.ClickToObject`, `Game.GetFreeBagSpace`, `Game.PickUpItemFromItemPack`.

Consequence: không cần mở tay nải để biết bag còn chỗ.

## 18. `GameDialog` text-matching pattern đã tồn tại trong built-in FuBen auto

Status: **VERIFIED**

`AutoFight_FuBen` lấy current dialog, duyệt `Selections`, lowercase `selectionName`, so khớp với action text và gửi actual `selectionID:-1` qua `CMD_SHOW_GAMEDIALOG`.

Điều này là precedent rất mạnh cho NPC Trị liệu: match semantic text trong active dialog thay vì hardcode screen button/selection ID.

## 19. Trị liệu exact selection ID chưa phải static fact

Status: **VERIFIED về giới hạn dữ liệu hiện tại**

Không tìm thấy một global static Lua constant kiểu `TreatmentSelectionID`. Generic NPC dialog được server đưa xuống dưới dạng `Selections`.

Vì vậy future implementation phải đọc actual dialog selection và xác minh outcome, không được bịa một ID cố định.
