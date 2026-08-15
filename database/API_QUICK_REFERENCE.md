# API / Symbol Quick Reference

> Tra cứu nhanh cho AI. Đây không phải danh sách mọi method trong client; nó là các symbol có giá trị cao đã tìm thấy. `Existence` nghĩa symbol/name có bằng chứng; `Semantics` có thể VERIFIED/PROBABLE tùy mục.

## Lua core

| Namespace/Class | Member | Mục đích/diễn giải |
|---|---|---|
| `FGStudio.LuaSystem.LuaSystemManager` | `HasScript` | kiểm tra Lua script/UI đã load |
| | `GetScript` | lấy script instance/reference |
| | `LoadFromAssetBundle` | load Lua/script data từ bundle |
| | `LoadFromFolder` | load từ folder |
| | `ExecuteFunction` | invoke Lua function |
| | `OnReceivePacket` | inbound packet bridge |
| | `OnReceiveEvent` | inbound event bridge |
| | `SendPacketToServer` | outbound packet bridge |
| | `LuaEnv` | Lua environment property |

## Shared data / world queries

| Class | Member | Ghi chú |
|---|---|---|
| `LuaSystemSharedData` | `GetNearestNPC(npcResID)` | query NPC theo RESID |
| | `GetNearbySprites(includeDeath)` | nearby sprites, có option include dead |
| | `GetNearbyTeamLeaders` | team leaders nearby |
| | `GetNearTeammates(...)` | teammates, có low-HP priority/maxTargets args evidence |
| | `GetNearByEnemyIDs` | enemy IDs |
| | `GetNearByEnemies` | enemy objects/data |
| | `GetNearByPeacePlayers` | peace players |
| | `GetNearbyObjects` | generic nearby objects |
| | `GetLocalMapObjects` | local map object set |
| | `GetNearestItemPack` | nearest ground loot pack |
| | `GetNearbyItemPack` | nearby item packs |
| | `GetItems` | item collection |
| | `GetItemsAtSite(site)` | items in container/site |
| | `FindItems` / `FindItem` | item lookup |

## Game API — target / movement / NPC

| Class | Member | Ghi chú |
|---|---|---|
| `LuaSystemAPI_Game` | `ClickNPC(npcID)` | strong verified disassembly: stop auto path -> locate NPC -> orient/select -> SendClickOnObject |
| | `ClickToObject` | semantic object click |
| | `SelectTarget` | target selection |
| | `IsSelectTargetDie` | target dead query |
| | `ChaseTarget` | chase target |
| | `get_CurrentChaseTargetID` | current chased target ID |
| | `IsAllowDeadTarget` | dead-target policy |
| | `StopAutoPath` | stop auto path |
| | `HasPath(fromPos,toPos)` | path availability |
| | `CanMove` | move-state guard |
| | `IsMoving` | movement query |
| | `GetDistance` | distance helper |
| | `CellToDistance` | cell/distance conversion |
| | `CalculatePointOnLine` | geometry helper |
| | `DoLeap` / `DoJump` | movement/action |
| | `DoMeditate` | meditate action |
| | `DoAction(actionID)` | generic action |

## Game API — skill / buff / combat

| Member | Ghi chú |
|---|---|
| `GetAbilities` | ability collection |
| `GetAbilityLevel` | ability level |
| `GetAbilityTemplateData` | template data |
| `UseSkill(skillID)` | request/use skill API |
| `RequestUsingSkill` | skill request |
| `RequestUsingSkillWithPos` | positional skill |
| `RequestUsingSkillWithTarget` | target skill |
| `GetSkillLuaData` | Lua-facing skill data |
| `IsSkillRequireTarget` | target requirement |
| `CanUseSkill` | state guard |
| `GetBuffs` | buff collection |
| `GetBuffProperties` | buff properties |
| `HasBuff` | buff existence |
| `GetBuffData` | buff data |
| `GetTargetBuffIcons` | target buff display data |
| `SendRemoveBuff(buffID)` | remove/cancel buff request path |
| `GetCurrentHP` | current HP query |
| `IsRoleBusy` | busy-state guard |
| `IsLastActionOver` | action completion guard |

## Game API — auto

| Member | Ghi chú |
|---|---|
| `get_EnableAutoF1` / `set_EnableAutoF1` | built-in auto-related flag |
| `AutoRemoveFlag` | auto state flag helper |
| `AutoSetFlag` | auto state flag helper |
| `RangerAuto` | auto/range-related method evidence |
| `RangerRequest` | range/request related method |
| `DrawCicleAutoFight` | scene string, likely auto-fight radius marker |
| `RemoveAutoFightMark` | remove auto-fight marker |

Exact meaning of AutoF1/Ranger* must be runtime traced before production use.

## Game API — inventory/items

| Member | Ghi chú |
|---|---|
| `GetFreeBagSpace()` | free bag slots |
| `GetTotalItems` | item count/collection count |
| `GetItemData(dbID)` | item instance data by DB/instance ID context |
| `GetItemTemplateData` | static item template |
| `GetItemAtSite(site,pos)` | item at site/slot |
| `CountItem` | count item |
| `GetItemType(ItemID)` | item category |
| `GetEquipType(ItemID)` | equip category incl. Weapon |
| `GetPetEquipType` | pet equip category |
| `IsItemThrowable` | discard policy |
| `IsItemSellable` | sell policy |
| `IsItemSellToShopWithBoundMoney` | bound-money shop rule |
| `GetItemBasePrice` | base price |
| `GetItemBuyPrice` | buy price |
| `GetItemMaxStack` | stack max |
| `GetEquipStar` / `GetEquipLevel` | equipment properties |
| `GetGemType` / `GetGemLevel` | gem properties |
| `PickUpItemFromItemPack(itemPackID,slotIndex,UsingAuto)` | ground loot pickup |

## Item data fields/properties đã thấy

- `LuaItemData.ID` — instance ID
- `LuaItemData.ItemID` — template/resource ID
- `LuaItemData.Site`
- `LuaItemData.Position`
- `LuaItemData.Bound`
- `LuaItemData.Quantity`
- `LuaItemData.Durability`

## ItemType names

- `Equip`
- `CommonItem`
- `Gem`
- `Medicine`
- `PetEquip`

## EquipType names

- `Weapon`
- `Hat`
- `Cloth`
- `Gloves`
- `Shoes`
- `Belt`
- `Ring`
- `Necklace`
- `Mount`
- `Ring_2`
- `Amulet`
- `Amulet_2`
- `Cuff`
- `Shoulderpads`
- `Fashion`
- `Dart`
- `Soul`
- `DragonTattoo`
- `HeroicOrder`
- `Signet`
- `WeaponVisual`

Numeric enum values: **not recorded yet**.

## GUI API

| Class | Member | Ghi chú |
|---|---|---|
| `LuaSystemAPI_GUI` | `MainCallUI` | high-level UI/script call |
| | `CallUI` | UI/script call |
| | `CallUIAlwaysOnTop` | UI call with top behavior |
| | `MainFindUI` | find UI in main context |
| | `FindUI` | find UI |
| | `MainFindAllUIs` | enumerate main UIs |
| | `FindAllUIs` | enumerate UIs |
| | `Instantiate` | UI object instantiate |
| | `ShowMessageBox` | message box |
| | `ShowWaitingBox` | waiting UI evidence |
| `FGStudio.LuaSystem.GUI.UIButton` | `HandleClickEvent` | instance method; do not call with null/stale `this` |

## Network API

| Class/member | Ghi chú |
|---|---|
| `LuaSystemAPI_Network.SendPacket(packetID,data)` | outbound Lua network bridge |
| `LuaSystemManager.SendPacketToServer` | lower bridge target |
| `TCPGameEventProcessor.SendClickOnObject(objectID)` | ClickNPC disassembly path |

## Selected network command names

### World / object / movement

- `CMD_CHANGE_MAP`
- `CMD_NEW_OBJECTS`
- `CMD_REMOVE_OBJECTS`
- `CMD_OBJECT_LOAD_ALREADY`
- `CMD_CLICK_OBJECT`
- `CMD_OBJECT_DEATH`
- `CMD_REVIVE`
- `CMD_SYNC_DATA`
- `CMD_OTHER_SYNC_DATA`
- `CMD_AUTO_PATH`
- `CMD_MOVE_TO_LOCATION`
- `CMD_DO_ACTION`
- `CMD_DO_LEAP`
- `CMD_UPDATE_DYNAMIC_OBSTRUCTION_LABELS` (processor/string family)

### Inventory/shop/economy

- `CMD_UPDATE_MONEY`
- `CMD_ADD_ITEM`
- `CMD_UPDATE_ITEM`
- `CMD_SWAP_ITEMS`
- `CMD_REMOVE_ITEM`
- `CMD_UPDATE_ITEMS_LIST`
- `CMD_ITEM_PACK`
- `CMD_UPDATE_TRADER_STATE`

### Skill/combat/buff

- `CMD_ADD_SKILL`
- `CMD_REMOVE_SKILL`
- `CMD_REFRESH_SKILLS_CD`
- `CMD_USE_SKILL`
- `CMD_NEW_MISSILE`
- `CMD_NEW_SKILL_EXPLODE`
- `CMD_SKILL_DAMAGE`
- `CMD_SKILL_HEAL`
- `CMD_ADD_BUFF`
- `CMD_UPDATE_BUFF`
- `CMD_REMOVE_BUFF`
- `CMD_MOVESPEED_CHANGED`
- `CMD_DRAG_TARGET`
- `CMD_ACTIVATE_TRAP`
- `CMD_PUPPET_ATTACK`

### Tasks/team/social/state

- `CMD_ASSIGN_TASK`
- `CMD_COMPLETE_TASK`
- `CMD_UPDATE_TASK`
- `CMD_ABANDON_TASK`
- team data update commands
- faction updates
- title/repute commands
- `CMD_PK_VALUE`
- `CMD_CHAT_DATA`
- `CMD_CAPTCHA`
- `CMD_UPDATE_NAME`
- `CMD_VOICE_CHAT`
- `CMD_VOICE_REALTIME`
- `CMD_CLIENT_LUA`

Command existence does **not** determine packet direction or exact payload.

## World/scene symbols

### `FGStudio.Engine.Objects.GScene`

- `GetGroundHeight`
- `InSafeArea`
- `CanEnter`
- `ScreenToPosition`
- select-target decoration functions
- `DoSyncPosition`
- `DoVisionLogic`
- `DoCheckPetLogic`
- `get_PathFinder`
- role/pet/trap loading functions

### Data/classes

- `PathFinder`
- `NodeGrid`
- `LocalMapComponents`
- `NPCData`
- `MonsterData`
- `GrowPointData`
- `ZoneData`
- `PortalData`
- `MapAreaSoundData`
- `Obstructions`
- `DynamicObstructions`
- `Regions`
- `SafeAreas`

## Historic RVA hints for this frozen snapshot

Only for locating code in disassembler; prefer semantic resolve at runtime:

- `UIButton.HandleClickEvent` ~ `0x52D140`
- `LuaSystemManager.GetScript` ~ `0x516290`
- `LuaSystemManager.HasScript` ~ `0x516330`
- `LuaSystemAPI_Game.ClickNPC` ~ `0x66ADC0`
- `LuaSystemAPI_GUI.CallUI` ~ `0x6A5CD0`
- `LuaSystemAPI_GUI.MainCallUI` ~ `0x6A5E70`
- `LuaSystemAPI_GUI.FindUI` ~ `0x6A5DF0`
- `LuaSystemAPI_GUI.MainFindUI` ~ `0x6A5F90`
- `LuaSystemAPI_Network.SendPacket` ~ `0x6A69A0`

## Runtime safety reminder

- Read-only metadata/scanner != mutable Unity action.
- UI/GameObject/Lua actions should run through validated Unity/main-thread path.
- Do not cache UI object pointers across UI reconstruction/loading.
- After any server-authoritative mutation, observe/rescan state before next mutation.
