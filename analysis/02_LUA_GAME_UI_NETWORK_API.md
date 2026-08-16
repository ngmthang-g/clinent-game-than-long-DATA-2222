# Lua runtime / Game API / GUI API / Network API — current semantic map

> `Interface.unity3d` has now been decoded and yielded readable Lua source plus UI layouts. Therefore this document distinguishes what is directly recovered from Lua/runtime from what still needs targeted live proof.

---

## 1. Lua is a first-class gameplay orchestration layer

The client is not simply “C# compiled to IL2CPP”. It also has a substantial Lua subsystem under `FGStudio.LuaSystem`.

Recovered architecture:

```text
IL2CPP game/runtime state
 -> LuaSystemSharedData / LuaSystemAPI_Game
 -> readable Lua gameplay/UI scripts
 -> LuaSystemAPI_GUI / LuaSystemAPI_Network
 -> server request / runtime action
 -> inbound packet/event
 -> Lua/UI/runtime state update
```

This means many actions that look like visible button clicks are better understood from the Lua handler and semantic API call than from `UIButton.HandleClickEvent` itself.

---

## 2. `LuaSystemManager`

Class:

`FGStudio.LuaSystem.LuaSystemManager`

High-value members recovered from metadata/native evidence include:

- `CreateTable`
- `OnReceiveEvent`
- `OnReceivePacket`
- `SendPacketToServer`
- `HasScript`
- `GetScript`
- `LoadFromAssetBundle`
- `LoadFromFolder`
- `ExecuteFunction`
- `get_LuaEnv` / `set_LuaEnv`
- `Reload`
- `RegisterLibraries`
- `RegisterConstants`.

`Interface.unity3d` extraction confirms `LoadFromAssetBundle` was not just a theoretical clue: the shipped client really contains readable Lua script TextAssets.

Use `HasScript` / `GetScript` to reason about current script/UI lifetime instead of assuming a fixed delay made a panel ready.

---

## 3. `LuaSystemSharedData` — semantic state/query layer

High-value query/member names include:

- `get_LeaderRoleData`
- `GetNearestItemPack`
- `GetNearestNPC`
- `GetNearbySprites`
- `GetNearbyTeamLeaders`
- `GetNearTeammates`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyItemPack`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetDeviceInfo`
- `GetItems`
- `FindItems`
- `FindItem`
- `GetItemsAtSite`.

Related world-data names include NPC/monster/pet/grow-point/portal/zone data.

### Runtime schemas already solved through shipped Lua/UI

#### Nearby peaceful players

`Game.GetNearByPeacePlayers(limit)` supplies at least:

- RoleID
- Name
- Level
- FactionID
- HP
- MaxHP
- GuildName
- AvartaID
- TeamRank.

#### Nearby enemies

Shipped enemy UI consumes the same core identity/vital fields.

#### Team

`C_TeamData.TeamMember[]` contains at least:

- RoleID
- RoleName
- Level
- FactionID
- MapID
- Hp
- MaxHp
- AvartaID
- PosX
- PosY.

Therefore old statements that “return type/field layout is entirely unknown” are obsolete. Only **additional** fields beyond the schemas already consumed by shipped code remain targeted research.

---

## 4. `LuaSystemAPI_Game` — primary semantic Game layer

### Target / NPC / world

Important members:

- `ClickNPC(npcID)`
- `ClickToObject`
- `SelectTarget`
- `IsSelectTargetDie`
- `get_CurrentChaseTargetID`
- `ChaseTarget`
- `IsAllowDeadTarget`
- `StopAutoPath`
- `GetNPCPosition`
- `GetCurrentMoveDestination`.

Direct native evidence for `ClickNPC` shows:

```text
StopAutoPath
 -> resolve NPC/object
 -> orient/select target
 -> SendClickOnObject(objectID)
```

Historic frozen RVA ~`0x66ADC0` is a disassembly locator only.

### Movement / map

Semantic members observed/used by shipped Lua include:

- `CanMove`
- `IsMoving`
- `HasPath`
- `MoveTo`
- `MoveToEx`
- `GoTo`
- `GetDistance`
- `CellToDistance`
- `CalculatePointOnLine`
- `IsMapReady`
- `DoLeap`
- `DoJump`
- `DoMeditate`
- `DoAction`.

Built-in `GoToNPC(mapID,npcID)` already demonstrates the preferred NPC route:

```text
Game.GoTo(map,-1,-1) if map change needed
 -> Game.GetNPCPosition(npcID)
 -> Game.GoTo(map,X,Y)
 -> semantic NPC interaction
```

Do not invent NPC coordinates from static Config when runtime position lookup exists.

### Skill / ability

High-value members:

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
- `GetSkillCooldown(skillID)`.

Shipped SkillBar calls `Game.UseSkill(skillID)` directly.

`GetSkillCooldown(skillID)` returns passed/cooldown ticks, so physical F-key slots are not required to identify or time a skill.

### Buff

- `GetBuffs`
- `GetBuffProperties`
- `HasBuff`
- `GetBuffData`
- `GetTargetBuffIcons`
- `SendRemoveBuff`.

`GetBuffs()` records are verified to expose BuffID, DurationTick in milliseconds and Stack.

### Inventory / item

- `GetFreeBagSpace`
- `GetTotalItems`
- `GetItemTemplateData`
- `GetItemData`
- `GetItemAtSite`
- `GetItemsAtSite`
- `CountItem`
- `GetItemType`
- `GetEquipType`
- `GetPetEquipType`
- `IsItemThrowable`
- `IsItemSellable`
- `IsItemSellToShopWithBoundMoney`
- price/stack/equip/gem helpers
- `PickUpItemFromItemPack`.

Live item identity:

`ID = instance`, `ItemID = template`, `Site = container`, `Position = slot`.

### Other state/helpers

Observed APIs include:

- `GetCurrentHP`
- `IsRoleBusy`
- `IsLastActionOver`
- `CanUseItem`
- `IsProgress`
- `SendAnswerCaptcha`
- `CheckCondition`
- appearance/faction helpers.

---

## 5. Built-in Auto Fight semantic layer

Interface Lua extraction resolves the major auto modes:

`C_AutoModel`:

- None = 0
- Train = 1
- PK = 2
- Quest = 3
- AutoPath = 4
- Fllow = 5
- FuBen = 6.

Train start:

`GUI.FindUI("AutoFight_Main"):StartAutoFight(C_AutoModel.Train)`.

Train stop:

`StartAutoFight(C_AutoModel.None)`.

The visible `Đánh quái` tab is a configuration UI, not the semantic start action.

Canonical detail: `analysis/10_BUILTIN_AUTO_FIGHT_ENGINE.md`.

---

## 6. `LuaSystemAPI_GUI`

High-value members:

- `Instantiate`
- `MainCallUI`
- `MainFindUI`
- `MainFindAllUIs`
- `CallUI`
- `CallUIAlwaysOnTop`
- `FindUI`
- `FindAllUIs`
- `ShowMessageBox`
- `ShowWaitingBox`.

Historical disassembly showed `MainCallUI`/`CallUI` flowing through `MonoBehaviourExecutor` script/UI resolution.

Frozen RVA hints remain diagnostic only:

- `MainCallUI` ~ `0x6A5E70`
- `CallUI` ~ `0x6A5CD0`
- `MainFindUI` ~ `0x6A5F90`
- `FindUI` ~ `0x6A5DF0`.

### Layout -> Lua handler -> action is now directly available

Recovered 338 layout XMLs and 1,469 handler bindings allow future AI to start from the visible panel/button and follow the actual Lua callback.

Examples:

- `Revival_Layout` -> exact revive handlers;
- `NPCShop_SellItemTab_Layout` -> sell UI logic;
- `RoleInfo_BagTab_Layout` -> item/sort actions;
- `GameDialog_Layout` -> dynamic function buttons;
- `AutoFight_Layout` / `AutoTrainMonster_Layout` -> auto settings/start distinction.

Canonical callback index: `database/UI_LAYOUT_CALLBACKS.md`.

---

## 7. `UIButton.HandleClickEvent` — lifecycle warning

Class:

`FGStudio.LuaSystem.GUI.UIButton`

`HandleClickEvent` is a native **instance method** and dereferences object state.

Consequences:

- null `this` is invalid;
- a pointer from an old UI state may be stale after panel reconstruction;
- do not cache UIButton pointers across loading/map/UI transitions;
- semantic Lua/UI resolution at action time is safer than replaying a stale native button instance.

Correct pattern:

```text
action A
 -> wait concrete state/event
 -> resolve current script/UI/semantic action B
 -> dispatch B in valid game context
 -> observe result
```

A fixed `Sleep` is only a timeout, never UI-ready proof.

---

## 8. `LuaSystemAPI_Network`

`SendPacket(packetID,data)` bridges to:

`LuaSystemManager.SendPacketToServer(packetID,data)`.

Frozen RVA hint ~`0x6A69A0`.

Interface extraction also recovered `TCPPacketDefine` with **169 exact symbolic packet IDs**.

Full list:

`database/PACKET_IDS.csv`.

### Exact actions already solved from legitimate Lua construction

#### Shop sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

`itemInstanceID:NpcShopID:ShopID`

#### Dynamic GameDialog

`CMD_SHOW_GAMEDIALOG = 100007`

`selectionID:SelectedItemID`

#### Revive

`CMD_REVIVE_DATA = 200063`

- normal/Đầu thai = 1
- newbie = 2
- skill = 3.

#### Bag/item

`CMD_ITEM_ACTION = 100005`

observed Equip/Use/Abandon/Move/Split actions.

`CMD_BAG_SORT = 100006`.

Use `database/NETWORK_COMMAND_CATALOG.md` for the evidence-level distinction between symbol-only, exact ID, exact request payload and full request/response lifecycle.

---

## 9. GameDialog is server/runtime-driven, not a fixed button map

Recovered Lua proves:

`Selections[selectionID] = visibleText`.

The UI stores the current selection ID in the generated button/tag and sends the actual ID back.

Built-in FuBen automation already contains a text-matching pattern against active selection names.

Therefore a service such as `Trị liệu` should be resolved from the **active current GameDialog text**, not from a guessed permanent selection ID or stale UIButton pointer.

---

## 10. Preferred research order for an unresolved visible action

If a user names a visible feature/button that is not documented:

```text
1. locate <Panel>_Layout handler binding
2. open the same-name Lua script
3. identify Game/GUI/Network call
4. identify exact packet payload only if Lua constructs one
5. identify inbound event/state proof
6. native reverse only if one exact semantic gap remains
```

This replaces the older advice to immediately trace `MainCallUI`/`SendPacket` for every case. Manual/runtime tracing is now reserved for values that are actually server-dynamic or absent from shipped Lua.

---

## 11. Confidence state after Phase 2/3

### VERIFIED

- Lua subsystem/classes and readable shipped source;
- 339 Lua classes + global infrastructure;
- 338 layouts + 1,469 bindings;
- nearby peaceful/enemy player schemas consumed by UI;
- team member schema consumed by UI;
- semantic movement/NPC/item/skill/buff APIs;
- Auto Train semantic start;
- exact shop sell/revive/GameDialog/bag action contracts documented elsewhere;
- dynamic dialog mechanism.

### Still targeted runtime proof

- actual server-supplied `Trị liệu` selection for a specific live healer/state;
- server acceptance of specific beneficial skills on non-team peaceful players;
- additional actor fields not already consumed by shipped UI/Lua;
- final external execution-bridge proof if implementation work is requested.

Do not resurrect solved Lua/UI/action questions as PROBABLE merely because this document was originally written before Interface extraction.
