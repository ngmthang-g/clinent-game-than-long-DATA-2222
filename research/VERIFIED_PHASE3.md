# VERIFIED Phase 3 — UI/runtime semantic findings

> Source evidence: decrypted Interface Lua/layouts + Config XML + runtime metadata inspection + direct frozen-snapshot GameAssembly disassembly. These findings materially reduce the need for CE scans, screen clicks and fixed delays.

## 1. Nearby peaceful-player schema is directly exposed to shipped UI

Status: **VERIFIED**

`MainUI_NearByPlayers_PlayersTab` calls `Game.GetNearByPeacePlayers(MaxPlayers)` and reads RoleID, Name, Level, FactionID, HP, MaxHP, GuildName, AvartaID and TeamRank. The stock UI targets a selected record using `Game.SelectTarget(RoleID)`.

Conclusion: nearby friendly HP/MaxHP/name/RoleID/faction/guild does not require party membership, OCR or arbitrary HP memory scanning.

## 2. Nearby enemy UI exposes the same core schema

Status: **VERIFIED**

`Game.GetNearByEnemies(false,true,MaxPlayers)` feeds Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank/RoleID to the enemy UI.

## 3. Selected target is a rich semantic object

Status: **VERIFIED**

`Game.SelectedTarget` is consumed with at least RoleID, Type, Avarta, Name, HPPercent, MPPercent, RagePercent, EnergyPercent, Level, FactionID and MonsterBelongState depending on target type.

`Game.GetTargetBuffIcons(RoleID)` exposes target buff icons. `OtherRolePopup` additionally reads TeamID, GroupID, GuildID, GuildRank and AlliesID for selected players.

## 4. Exact Auto Train UI wrapper is solved

Status: **VERIFIED**

`TopIcon:AutoTrainClick()` finds `AutoFight_Main` and calls `StartAutoFight(C_AutoModel.Train)`. `AutoStopClick()` calls `StartAutoFight(C_AutoModel.None)`.

Visible `Đánh quái` inside the Auto settings window is a settings tab, not the semantic Train start action.

## 5. Skill cooldown is semantic data

Status: **VERIFIED**

`Game.GetSkillCooldown(skillID)` returns passedTicks and cooldownTicks. Ready when cooldown<=0 or passed>=cooldown.

The SkillBar executes the tagged SkillID through `Game.UseSkill(skillID)`, proving physical F-key identity is not required for semantic casting.

## 6. QuickSkills mapping is structured

Status: **VERIFIED**

`Game.RoleData.QuickSkills` serializes `position_skillID` entries. Five UI pages use position groups 0..9, 100..109, 200..209, 300..309 and 400..409.

Saving uses `CMD_SAVE_QUICK_SKILLS = 100009` with Position/SkillID records.

## 7. Runtime local buff schema is exposed

Status: **VERIFIED**

`Game.GetBuffs()` records expose BuffID, DurationTick (milliseconds) and Stack. `Game.GetBuffData(BuffID)` exposes at least BuffID/Level/Stack. `Game.GetBuffProperties` exposes magic attributes. Add/Update/Remove buff events update the BuffFrame.

## 8. Nga My donor skill identity correction

Status: **VERIFIED by cross-source comparison**

Actual `Skills.xml`:

- 406 Phật Quang Phổ Chiếu
- 407 Xung Hư Dưỡng Khí
- 408 Khởi Tử Hồi Sinh
- 423 Kim Châm Độ Kiếp
- 424 Thanh Tâm Phổ Thiện Chú.

Legacy Lua variable `C_NMBuff.KIMCHAMDOKIEP = 407` is misleading. `AutoHp_Layout` visibly labels that toggle Xung Hư Dưỡng Khí. Therefore actual Kim Châm is 423, not 407.

Built-in AutoHp fallback is 406 -> 424 -> 407.

## 9. Built-in Nga My team-heal action donor is exact

Status: **VERIFIED**

The engine reads teammate IsDeath/HP/MaxHP/Position/RoleID, checks skill condition, derives CastRange from skill data, chases via `Game.ChaseTarget` if needed, then uses `Game.RequestUsingSkillWithTarget`.

## 10. Bag UI is structured and event-driven

Status: **VERIFIED**

`BagItemsGrid` has 100 logical slots but reads actual contents with `Game.GetItemsAtSite(Site)` and positions records by `dbItemData.Position`.

AddItem/RemoveItem/UpdateItemsList events update all bag grids. RemoveItem data contains site/dbID/position.

## 11. NPCShop current state supplies exact sell identifiers

Status: **VERIFIED**

`NPCShop_SellItemTab` uses current NpcShopID and ShopID (`CurrentShopData.ID`) and sends `CMD_NPC_SHOP_SELL_REQUEST=200036` with `itemInstanceID:NpcShopID:ShopID`.

Quick Sell is only a UI convenience calling the same request.

## 12. Revival data exposes exact countdown/availability

Status: **VERIFIED**

Revival data used by Lua contains TimeLeft, IsEnableReviveNewbie, IsEnableBySkill and server Action state in inbound lifecycle. When countdown expires, stock UI automatically sends normal/Đầu thai type 1.

## 13. Progress state is event-driven

Status: **VERIFIED**

Events BeginProgress=12, InteruptProgress=13 and UpdateProgressTime=14 drive ProgressBar duration/lifetime state in milliseconds.

## 14. Captcha is an explicit user-verification state

Status: **VERIFIED**

NewCaptcha=57 opens Captcha with question/image/answer choices and manual submit uses `Game.SendAnswerCaptcha`.

Automation design rule: pause and require user input; do not implement auto-solving/bypass.

## 15. Map readiness and object APIs are semantic

Status: **VERIFIED**

Minimap/local map use `Game.IsMapReady()`, `Game.GetMapName()`, `Game.GetMapSize()`, `Game.GetLocalMapObjects()`, `Game.GetNearbyObjects()`, `Game.GetCurrentMoveDestination()`, `Game.MoveTo(X,Y)` and `Game.GoTo(MapID,-1,-1)`.

## 16. MainThread internal dispatcher chain is fully resolved

Status: **VERIFIED by metadata + direct GameAssembly disassembly**

Class:

`FGStudio.Engine.Utilities.MainThread`

Exact frozen-snapshot method RVAs:

- `Awake` = `0x601130`
- `DoExecuteWorks` = `0x601190`
- `Execute(System.Action)` = `0x601250`
- `Update` = `0x6012D0`
- `.ctor` = `0x6012E0`
- `get_Instance` = `0x601360`
- `set_Instance` = `0x6013A0`.

The constructor creates `ConcurrentQueue<System.Action>` and stores it at `this+0x20` (`waitToBeProcess`).

`Awake()` stores `this` into the static Instance backing field.

`Execute(Action)` loads `[this+0x20]` and enqueues the supplied Action into that concurrent queue.

`Update()` directly dispatches to `DoExecuteWorks()`.

`DoExecuteWorks()` checks queue-empty state, dequeues Actions and invokes returned delegates, looping until the queue is empty.

Therefore the game-owned path is exactly:

`Execute(Action) -> ConcurrentQueue.Enqueue -> Unity Update -> DoExecuteWorks -> TryDequeue -> Action.Invoke`.

Canonical detailed evidence: `analysis/21_MAIN_THREAD_DISPATCHER.md`.

### Remaining distinction

The **dispatcher itself is solved**. The external tool has not yet proven the final live bridge step of constructing/rooting a valid managed `System.Action`, calling `MainThread.Instance.Execute(action)` and observing the callback on Unity Update thread. Keep that as a targeted runtime implementation proof, not as uncertainty about the dispatcher internals.

## Phase 3 design consequence

The remaining engineering bottleneck is now narrower:

1. stable live resolution of `MainThread.Instance`;
2. safe managed `System.Action` construction/lifetime from the external bridge;
3. one harmless end-to-end callback/thread-ID proof;
4. state-machine integration;
5. a few server-driven dynamic choices such as NPC treatment GameDialog selection.
