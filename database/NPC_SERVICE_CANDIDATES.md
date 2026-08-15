# NPC service candidates — offline semantic inference

> **Status:** IDs/names/maps/ResName are VERIFIED static data. Service tags in this document are **PROBABLE inference** from Vietnamese names + repeated `ResName` archetypes. Do not invoke a service solely from this tag; confirm actual `GameDialog`/shop data at runtime.

## 1. Healer / physician candidates

### `LangZhong1/2` family

This is the strongest static healer archetype candidate. `LangZhong` semantically corresponds to physician/doctor, and many NPC display names are explicitly medical.

| NPC ID | Name | ResName | Map |
|---:|---|---|---|
| 140 | Phó Đương Quy | LangZhong1 | Đại Lý (2) |
| 279 | Dược Đại Phu | LangZhong1 | Hỏa Diệm Sơn (55) |
| 308 | Ông Thúc Chi | LangZhong1 | Long Tuyền (27) |
| **337** | **Đỗ Bất Đằng** | **LangZhong1** | **Lâu Lan (5)** |
| **338** | **Đỗ Hoàng Đằng** | **LangZhong1** | **Lâu Lan (5)** |
| **339** | **Đỗ Thanh Đằng** | **LangZhong1** | **Lâu Lan (5)** |
| 443 | Trương Minh Cảnh | LangZhong1 | Lạc Dương (3) |
| 450 | Nghiêm Bách Thảo | LangZhong1 | Lạc Dương (3) |
| 456 | Kha Bách Nhân | LangZhong1 | Lạc Dương (3) |
| 613 | Lục Tùng | LangZhong1 | Tung Sơn (23) |
| 636 | Bàng Thông | LangZhong2 | Tô Châu (4) |
| 676 | Trình Viễn Trí | LangZhong1 | Tô Châu (4) |
| 686 | Hồ Phồn | LangZhong1 | Tô Châu (4) |
| 690 | Bình Sa Nhan | LangZhong1 | Tô Châu (4) |
| 691 | Chu Phòng Phong | LangZhong1 | Tô Châu (4) |
| 1 | Diêu Phu | LangZhong1 | Bảo Tàng Động Tầng 1 (50) |
| 5 | Đỗ Bất Đằng | LangZhong1 | Ngân Ngai Tuyết Nguyên (47) |
| 6 | Chu Du | LangZhong1 | Ngân Ngai Tuyết Nguyên (47) |
| 152 | Lâm Tăng | LangZhong2 | Đại Uyển (71) |
| 153 | Lan Tác An | LangZhong2 | Đại Uyển (71) |

### `MingYi1/2` family

Second strong medical/doctor candidate family (`MingYi`, nhiều NPC tên “Du Y”, “Bách Thảo”). Examples:
- 80 Đàm Cảnh Thiên — Đại Lý
- 102 Bạch Triển Nguyên — Đại Lý
- 105 Đào Tiên Thu — Đại Lý
- 175 Giang Hồ Du Y — Đôn Hoàng
- 440/442 Bạch Dĩnh Minh — Lạc Dương
- 458 Long Tam Thiếu — Lạc Dương
- 517 Nhạc Trọng Thu — Nam Hải
- 783 Giang Hồ Du Y — Vô Lượng Sơn
- 812 Tô Phi — Tây Hồ.

### Explicit treatment object

- NPC `912` = **Tháp trị liệu**, `ResName=ZhiLiaoTa`.

This proves the client vocabulary explicitly contains a treatment/heal object archetype, but NPC 912 has no current static AutoPath MapID mapping and is not automatically the normal city-healer service.

## 2. Recovery/healing service candidates in KVK/Phụng Minh

`ResName=npckvkZhuChengHuiFu20110811` (“HuiFu” = recovery) occurs on:
- 225 Mục Hồi Xuân
- 226 Mục Nghênh Xuân
- 227 Mục Vân Xuân
- 230 Mục Dương Xuân
- 233 Mục Hoa Xuân

All map to Phụng Minh Trấn (Map 1). This is another strong semantic recovery-service family.

## 3. Merchant/vendor candidates

Repeated vendor archetypes include:
- `ShangRen`
- `PangDaShangRen`
- `PangBanShangRen`
- `JiuDianLaoBan1/2/3`
- specialized KVK names containing `ShangRen`.

These are good **candidate discovery tags** for a shop/service search, but they do not prove the NPC opens a sell-capable `NPCShop`. Runtime proof should be `GameDialog` selection -> inbound `CMD_NPC_SHOP_DATA` -> `NPCShop`.

Examples:
- Đại Lý: 64 Phụng Triều Dương, 86 Sơ Kích Bình, 87 Kim Ngũ Gia, 90 Hà Sinh Kim, 130 Tôn Bát Gia.
- Lạc Dương: 434 Kiều Phúc Thịnh, 452 Hà Sinh Tài, 454 Kim Lục Gia.
- Tô Châu: 646 Bao Thế Vinh, 669 Tô Song, 688 Trương Tiến Bảo, 695 Phạm Đại Thành.
- Lâu Lan: 341 Hiệp Hàng has `npcXiYuTuoDuiShangRen` (caravan merchant archetype).

### Inn/shop-owner archetype

`JiuDianLaoBan1/2/3` appears on 20 NPCs, including “Hắc Thi Thương Nhân” in Đôn Hoàng, Kiếm Các, Kính Hồ, Tung Sơn, Thái Hồ, Vô Lượng Sơn and various city shop/inn owners.

## 4. Blacksmith/repair candidate family

`ResName=TieJiang` appears on 13 NPCs, including:
- 94 Đồng Hóa Kim — Đại Lý
- 95 Quá Tam Chùy — Đại Lý
- 398 Chu Thập Tam — Lâu Lan
- 430 Vương Đức Quý — Lạc Dương
- 663 Chu Phong — Tô Châu
- 708 Trương Tiểu Tuyền — Tô Châu
- 709 Trương Tiểu Hà — Tô Châu
- 710 Tiết Chúc — Tô Châu
- 866 Phong Hồ Tử — Lạc Dương.

Likely use: equipment-related/repair/crafting service candidate. Confirm dialog before action.

## 5. Warehouse/storage candidate clue

NPC 219 Bao Mãn Xương has `ResName=npckvkZhuChengCangKu110812` (`CangKu` = warehouse) on Phụng Minh Trấn. Static semantic evidence is strong for storage role, but exact command/service should still be runtime-confirmed.

## 6. How future AI should use this file

1. Filter NPC candidates by current map and semantic family.
2. Route using `Game.GetNPCPosition(npcID)` — **not** a guessed static coordinate.
3. Interact using internal Game/Lua action.
4. Inspect actual `GameDialog.Selections` or wait for `NPCShop` data.
5. Promote a candidate to VERIFIED service mapping only after repeatable runtime evidence.

### Important Lâu Lan treatment candidate

The frozen Config database **does confirm `Đỗ Thanh Đằng = NPC ID 339, LangZhong1, Map 5 Lâu Lan`**. This makes 339 a strong healer candidate, but it does not by itself prove the exact server selection text/ID for “Trị liệu”.
