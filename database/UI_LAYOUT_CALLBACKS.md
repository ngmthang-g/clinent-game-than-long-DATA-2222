# High-value UI layouts and callbacks

Source: decrypted `Interface.unity3d`. Recovered **338 XML UI layout TextAssets** and **1,469 handler bindings** (`ClickHandler`, `SelectHandler`, hover/value/text handlers, etc.).

## `Revival_Layout`

| Visible text | Handler |
|---|---|
| Tân thủ | `ButtonNewbieReviveClicked` |
| Hồi sinh | `ButtonSkillReviveClicked` |
| Đầu thai | `ButtonGoToInfernalClicked` |
| Mở khung Chat | `ButtonOpenChatBoxClicked` |

## `AutoFight_Layout`

Tabs are wired through `ToggleTabHeaderSelected`. Components/tabs include `AutoTrainMonster` (visible Đánh quái), PickUp, Pet, PK, AutoHp/Hồi phục, FuBen and Utilities. Other important handlers: `ButtonResetAutoClicked`, `ButtonSaveSettingsClicked`.

## `AutoTrainMonster_Layout`

Handlers/settings include:
- monster whitelist: `BtnListMonsterAttackClick`, add/delete/refresh/save handlers;
- scan/lure/radius: `TogLureMonsterTriger`, `TogAttackInRadiusTriger`, `InputLimitRadius`;
- skill slots: `BtnSkill_1Click` … `BtnSkill_7Click`;
- combo/basic-skill toggles.

Important: selecting this tab is configuration; semantic train start is `AutoFight_Main:StartAutoFight(C_AutoModel.Train)`.

## `NPCShop_Layout`

Buy/sell tabs use `ToggleTabHeaderSelected`.

`NPCShop_SellItemTab_Layout` contains quick-sell UI (`Bán vật phẩm nhanh`) and sell/buy-back controls. Exact network sell payload is in `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`.

## `RoleInfo_BagTab_Layout`

| Visible text | Handler |
|---|---|
| Bày bán | `ButtonStartStallClicked` |
| Gộp vật phẩm | `ButtonMergeItemsClicked` |
| Sắp xếp | `ButtonSortBagClicked` |
| Thiết lập dùng nhanh | `ButtonOpenSetQuickItemsClicked` |
| Túi bảo thạch | `ButtonOpenGemBagClicked` |
| Túi thời trang | `ButtonOpenFashionBagClicked` |
| Túi đá Võ Hồn | `ButtonOpenSoulStoneBagClicked` |

## `MessageBox_Layout`

| Visible text | Handler |
|---|---|
| Xác nhận | `ButtonOKClicked` |
| Hủy bỏ | `ButtonCancelClicked` |

Lua stores `OKCallback` / `CancelCallback`; the semantic callback flow is preferred over holding native UIButton pointers.

## `GameDialog_Layout`

Dynamic function buttons use `FunctionButtonClicked`. The Lua script creates these from server-provided `Selections` and stores `selectionID` in the button Tag.

## `AutoHp_Layout`

Contains controls/settings for HP/MP recovery, auto comeback, auto revival, Nga My buff/heal threshold, Cải Tử Hoàn Sinh, Phật Quang Phổ Chiếu, Thanh Tâm Phổ Thiện Chú and Kim Châm Độ Kiếp.

## `Utilities_Layout`

Contains team/trade/mount/emoji reject behavior, auto level-up and up to 20 auto-buff skill slots.

## General rule

When a task names a visible button or panel, search `<Name>_Layout` plus the same-name Lua script first. Layout gives presentation/binding; Lua gives actual action, state and packet semantics.