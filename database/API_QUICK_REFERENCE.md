# API / Symbol Quick Reference — frozen client

> Compact lookup for future AI. This is not every method in the client. It records **high-value semantic APIs and exact facts already recovered** so features do not restart from binary scans.

Evidence labels inside notes matter. For broad subsystem routing use `database/SUBSYSTEM_SOURCE_MAP.md`.

---

# 1. Lua core

## `FGStudio.LuaSystem.LuaSystemManager`

High-value members:

- `HasScript`
- `GetScript`
- `LoadFromAssetBundle`
- `LoadFromFolder`
- `ExecuteFunction`
- `OnReceivePacket`
- `OnReceiveEvent`
- `SendPacketToServer`
- `LuaEnv`.

Role:

managed/native bridge into embedded Lua system.

Shipped Interface bundle contains readable Lua source, so before disassembling a Lua-driven feature, search its Lua script/layout first.

---

# 2. SharedData / world queries

## `FGStudio.LuaSystem.LuaSystemSharedData`

High-value queries:

- `GetNearestNPC(npcResID)`
- `GetNearbySprites(includeDeath)`
- `GetNearbyTeamLeaders`
- `GetNearTeammates(...)`
- `GetNearByEnemyIDs`
- `GetNearByEnemies(...)`
- `GetNearByPeacePlayers(limit)`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetNearestItemPack`
- `GetNearbyItemPack`
- `GetItems`
- `GetItemsAtSite(site)`
- `FindItems`
- `FindItem`
- `get_LeaderRoleData`.

## Nearby peaceful player schema — VERIFIED from shipped UI

`Game.GetNearByPeacePlayers(limit)` supplies at least:

- `RoleID`
- `Name`
- `Level`
- `FactionID`
- `HP`
- `MaxHP`
- `GuildName`
- `AvartaID`
- `TeamRank`.

Do not rediscover those fields through CE/OCR.

## Nearby enemy schema — VERIFIED

Shipped enemy UI reads the same core identity/vital fields from `GetNearByEnemies(...)`.

## Team state — VERIFIED

`C_TeamData.TeamMember[]` fields observed:

- `RoleID`
- `RoleName`
- `Level`
- `FactionID`
- `MapID`
- `Hp`
- `MaxHp`
- `AvartaID`
- `PosX`
- `PosY`.

---

# 3. Selected target / social state

`Game.SelectedTarget` is a structured semantic object.

Fields consumed by shipped UI include, depending on target type:

- `RoleID`
- `Type`
- `Avarta`
- `Name`
- `HPPercent`
- `MPPercent`
- `RagePercent`
- `EnergyPercent`
- `Level`
- `FactionID`
- `MonsterBelongState`.

Selected-player popup additionally exposes social IDs such as TeamID/GroupID/GuildID/GuildRank/AlliesID.

`Game.GetTargetBuffIcons(RoleID)` exposes target buff display icons.

---

# 4. Game API — movement / target / NPC

## `FGStudio.LuaSystem.API.LuaSystemAPI_Game`

High-value members:

- `ClickNPC(npcID)`
- `ClickToObject(objectID)`
- `SelectTarget(roleID)`
- `IsSelectTargetDie`
- `ChaseTarget`
- `get_CurrentChaseTargetID`
- `IsAllowDeadTarget`
- `StopAutoPath`
- `HasPath(fromPos,toPos)`
- `CanMove`
- `IsMoving`
- `GetDistance`
- `CellToDistance`
- `CalculatePointOnLine`
- `MoveTo(X,Y)`
- `MoveToEx(...)`
- `GoTo(MapID,X,Y,callback)`
- `GetNPCPosition(npcID)`
- `IsMapReady()`
- `GetCurrentMoveDestination()`
- `DoLeap`
- `DoJump`
- `DoMeditate`
- `DoAction(actionID)`.

### `ClickNPC` direct native flow — VERIFIED

```text
StopAutoPath
 -> resolve NPC object
 -> orient/select
 -> TCPGameEventProcessor.SendClickOnObject(objectID)
```

Historic frozen RVA: ~`0x66ADC0`.

### Built-in `GoToNPC(mapID,npcID)` flow — VERIFIED from Lua

```text
if needed Game.GoTo(map,-1,-1)
 -> Game.GetNPCPosition(npcID)
 -> Game.GoTo(map,X,Y)
 -> find nearest NPC
 -> semantic interaction
```

Do not invent static NPC X/Y when this runtime path exists.

---

# 5. Game API — skill / combat / buff

Skill APIs:

- `GetAbilities`
- `GetAbilityLevel`
- `GetAbilityTemplateData`
- `UseSkill(skillID)`
- `RequestUsingSkill`
- `RequestUsingSkillWithPos`
- `RequestUsingSkillWithTarget`
- `GetSkillLuaData`
- `IsSkillRequireTarget`
- `CanUseSkill`
- `GetSkillCooldown(skillID)`
- `GetCurrentHP`
- `IsRoleBusy`
- `IsLastActionOver`.

## Cooldown — VERIFIED

`GetSkillCooldown(skillID)` returns:

- `passedTicks`
- `cooldownTicks`.

Ready when cooldown <= 0 or passed >= cooldown.

Shipped SkillBar calls `Game.UseSkill(skillID)`. Physical F-key position is presentation/configuration, not skill identity.

## Buff APIs

- `GetBuffs`
- `GetBuffProperties`
- `HasBuff`
- `GetBuffData`
- `GetTargetBuffIcons`
- `SendRemoveBuff(buffID)`.

### Local buff record — VERIFIED

`Game.GetBuffs()` exposes:

- `BuffID`
- `DurationTick` in milliseconds
- `Stack`.

`GetBuffData` exposes at least Level/Stack; `GetBuffProperties` exposes semantic magic properties.

---

# 6. Known Nga My support skill IDs

Frozen Config truth:

- `406` = Phật Quang Phổ Chiếu
- `407` = **Xung Hư Dưỡng Khí**
- `408` = Khởi Tử Hồi Sinh
- `423` = **Kim Châm Độ Kiếp**
- `424` = Thanh Tâm Phổ Thiện Chú.

Legacy Lua variable naming incorrectly suggests 407 is Kim Châm Độ Kiếp. Do not copy that bug.

Canonical: `database/NGAMY_SUPPORT_SKILLS.md`.

---

# 7. Built-in Auto Fight semantic entry

`C_AutoModel` verified values:

- None = 0
- Train = 1
- PK = 2
- Quest = 3
- AutoPath = 4
- Fllow = 5 (spelling preserved)
- FuBen = 6.

Train semantic start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

Stop:

`StartAutoFight(C_AutoModel.None)`.

Visible `Đánh quái` tab is configuration, not the start action.

---

# 8. Inventory / items

High-value runtime APIs:

- `GetFreeBagSpace()`
- `GetTotalItems`
- `GetItemData(dbID)`
- `GetItemTemplateData(ItemID)`
- `GetItemAtSite(site,pos)`
- `GetItemsAtSite(site)`
- `CountItem`
- `GetItemType(ItemID)`
- `GetEquipType(ItemID)`
- `GetPetEquipType`
- `IsItemThrowable`
- `IsItemSellable`
- `IsItemSellToShopWithBoundMoney`
- `GetItemBasePrice`
- `GetItemBuyPrice`
- `GetItemMaxStack`
- `GetEquipStar`
- `GetEquipLevel`
- `GetGemType`
- `GetGemLevel`
- `PickUpItemFromItemPack(itemPackID,slotIndex,UsingAuto)`.

## Live item identity — VERIFIED

- `LuaItemData.ID` = live database/instance ID
- `LuaItemData.ItemID` = template ID
- `Site` = logical container
- `Position` = slot
- `Bound`
- `Quantity`
- `Durability`.

Never confuse instance ID with template ID in mutation requests.

## ItemType semantic names observed

- Equip
- CommonItem
- Gem
- Medicine
- PetEquip.

## Equipment slot identity from static `Equips.xml`

`EquipPoint` exact positions include:

- 0 Weapon
- 1 Hat
- 2 Cloth
- 3 Gloves
- 4 Shoes
- 5 Belt
- 6 Ring
- 7 Necklace
- 8 Mount
- 11 Ring_2
- 12 Amulet
- 13 Amulet_2
- 14 Cuff
- 15 Shoulderpads
- 16 Fashion
- 17 Dart
- 18 Soul
- 19 DragonTattoo
- 20 HeroicOrder
- 21 Signet
- 22 WeaponVisual.

For “keep weapons”, static `EquipPoint==0` is the robust template test. Do not use only subtype `Type<10`.

---

# 9. Bag / shop / storage exact actions

## Bag site

`C_ItemSite.Bag = 10`.

Storage pages = 11..15.

## Item actions

`CMD_ITEM_ACTION = 100005`.

Observed actions:

- Equip = 1
- Use = 3
- Abandon = 4
- Move = 5
- Split = 8.

Storage move payload:

`5:itemInstanceID:destinationSite`.

## Bag sort

`CMD_BAG_SORT = 100006`.

Bag payload = `10`.

## NPC shop sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`.

Payload:

`itemInstanceID:NpcShopID:ShopID`.

Quick Sell uses this same semantic request.

Mutation rule:

`one current instance -> one request -> wait server/item proof -> rescan`.

---

# 10. Ground loot semantic engine

VERIFIED shipped flow uses:

- `GetNearbyItemPack`
- item-pack `RoleID` / `Position`
- `HasPath`
- `MoveToEx`
- `ClickToObject`
- `PickUpItemFromItemPack`.

Observed pick-all:

`Game.PickUpItemFromItemPack(itemPackID, -1, 1)`.

Do not rebuild loot detection from OCR.

---

# 11. Team / Follow

`C_TeamAction` verified values:

- CreateTeam = 0
- Kick = 1
- Disband = 2
- ChangLeader = 3
- LeaveTeam = 4
- AcceptJoin = 5
- RejectJoin = 6
- RequestJoin = 7
- AcceptInvite = 8
- RejectInvite = 9
- RequestInvite = 10.

Observed leave payload:

`4:selfRoleID`.

Built-in Follow:

`AutoFight_Main:TurnOnFollowTarget(RoleID)`.

Nearby target -> `MoveTo(Position)`; out-of-AOI teammate fallback can use `C_TeamData` MapID/PosX/PosY with `GoTo`.

---

# 12. Revive / NPC dialog

## Revive

`CMD_REVIVE_DATA = 200063`.

Types:

- normal / Đầu thai = 1
- newbie = 2
- skill revive = 3.

## Dynamic GameDialog

`Selections[selectionID] = visibleText`.

Submit:

`CMD_SHOW_GAMEDIALOG = 100007`

payload:

`selectionID:SelectedItemID`.

Usually `SelectedItemID=-1` when no reward item is selected.

There is **no verified universal static Trị liệu selection ID**.

---

# 13. GUI API

`FGStudio.LuaSystem.API.LuaSystemAPI_GUI`:

- `MainCallUI`
- `CallUI`
- `CallUIAlwaysOnTop`
- `MainFindUI`
- `FindUI`
- `MainFindAllUIs`
- `FindAllUIs`
- `Instantiate`
- `ShowMessageBox`
- `ShowWaitingBox`.

`FGStudio.LuaSystem.GUI.UIButton.HandleClickEvent` is an **instance method**; do not call it with null/stale `this` or cache button pointers across UI reconstruction.

Preferred feature investigation:

`<UI>_Layout -> same-name Lua -> semantic Game/GUI/Network action`.

---

# 14. Network API / exact packet lookup

`LuaSystemAPI_Network.SendPacket(packetID,data)` -> `LuaSystemManager.SendPacketToServer`.

Full exact 169 packet constants:

`database/PACKET_IDS.csv`.

High-value IDs:

- `CMD_ITEM_ACTION = 100005`
- `CMD_BAG_SORT = 100006`
- `CMD_SHOW_GAMEDIALOG = 100007`
- `CMD_SAVE_QUICK_SKILLS = 100009`
- `CMD_NPC_SHOP_DATA = 200034`
- `CMD_NPC_SHOP_BUY_REQUEST = 200035`
- `CMD_NPC_SHOP_SELL_REQUEST = 200036`
- `CMD_REVIVE_DATA = 200063`
- FuBen family 200168..200174 as documented.

Use `database/NETWORK_COMMAND_CATALOG.md` for evidence levels and subsystem grouping.

---

# 15. MainThread dispatcher

Class:

`FGStudio.Engine.Utilities.MainThread`.

VERIFIED frozen chain:

```text
Execute(System.Action)
 -> ConcurrentQueue<Action>.Enqueue
 -> Unity Update()
 -> DoExecuteWorks()
 -> dequeue
 -> Action.Invoke()
```

Queue field at frozen instance offset `+0x20`.

Frozen RVAs:

- `Awake` 0x601130
- `DoExecuteWorks` 0x601190
- `Execute` 0x601250
- `Update` 0x6012D0
- `.ctor` 0x6012E0
- `get_Instance` 0x601360
- `set_Instance` 0x6013A0.

Game-owned TCPGame/TCPLogin producers construct legitimate Actions and call Execute.

Use semantic resolution in production; historic RVA is a diagnostic locator only.

---

# 16. Static Config semantic scale

`Config.unity3d` is VERIFIED extracted into 75 XML TextAssets.

Important rows:

- Maps 193
- NPCs 1,003
- AutoPath 1,618
- Skills 2,091
- SkillProperties 2,044
- AutoSkills 300
- MagicAtrributes 509
- Items 5,238
- Equips 22,763
- Medicines 692
- Monsters 17,121
- Tasks 516
- GrowPoints 407
- Pets 8,349
- Spirits 1,889
- Factions 17
- FuBenScenarios 19.

Before opening static data, read `analysis/32_CONFIG_DOMAIN_ATLAS.md`.

---

# 17. World/scene native symbols

`FGStudio.Engine.Objects.GScene` observed methods include:

- `GetGroundHeight`
- `InSafeArea`
- `CanEnter`
- `ScreenToPosition`
- selection decoration functions
- `DoSyncPosition`
- `DoVisionLogic`
- `DoCheckPetLogic`
- `get_PathFinder`
- role/pet/trap loading functions.

Related types:

- `PathFinder`
- `NodeGrid`
- `LocalMapComponents`
- `NPCData`
- `MonsterData`
- `GrowPointData`
- `ZoneData`
- `PortalData`
- `Regions`
- `SafeAreas`
- `Obstructions`
- `DynamicObstructions`.

Target native world internals only when semantic APIs/config cannot answer the task.

---

# 18. Historic frozen RVA hints

Diagnostic only:

- `UIButton.HandleClickEvent` ~ `0x52D140`
- `LuaSystemManager.GetScript` ~ `0x516290`
- `LuaSystemManager.HasScript` ~ `0x516330`
- `LuaSystemAPI_Game.ClickNPC` ~ `0x66ADC0`
- `LuaSystemAPI_GUI.CallUI` ~ `0x6A5CD0`
- `LuaSystemAPI_GUI.MainCallUI` ~ `0x6A5E70`
- `LuaSystemAPI_GUI.FindUI` ~ `0x6A5DF0`
- `LuaSystemAPI_GUI.MainFindUI` ~ `0x6A5F90`
- `LuaSystemAPI_Network.SendPacket` ~ `0x6A69A0`.

Do not turn them into sole runtime identity.

---

# Runtime safety / usage rules

- read-only metadata/scanner != mutable Unity action;
- semantic values should be copied into external snapshots rather than retaining managed/UI pointers;
- UI/Game/Lua mutations belong on the validated game-owned main-thread dispatch path;
- do not cache UI object pointers across open/close/map/loading transitions;
- after server-authoritative mutation, observe/rescan state before next mutation;
- fixed delays are timeouts, not success proof;
- do not automatically solve/bypass Captcha.
