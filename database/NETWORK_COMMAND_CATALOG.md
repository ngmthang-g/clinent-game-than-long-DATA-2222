# Network Command / Event Catalog — refreshed after Lua packet extraction

> This file combines two evidence layers:
>
> 1. native/metadata command vocabulary (`CMD_*`, processor/event names);
> 2. decrypted Lua `TCPPacketDefine` with **169 exact numeric packet constants**.
>
> Full numeric list: `database/PACKET_IDS.csv`.
>
> Packet **ID existence does not prove direction or payload**. Exact payloads are VERIFIED only when legitimate Lua/native request code constructs them.

---

## 1. Core world / object lifecycle

Verified vocabulary includes:

- `CMD_CHANGE_MAP`
- `CMD_NEW_OBJECTS`
- `CMD_REMOVE_OBJECTS`
- `CMD_OBJECT_LOAD_ALREADY`
- `CMD_CLICK_OBJECT`
- `CMD_OBJECT_DEATH`
- `CMD_REVIVE`
- `CMD_SYNC_DATA`
- `CMD_OTHER_SYNC_DATA`
- `CMD_UPDATE_OBJECT_TITLE`
- `CMD_UPDATE_NAME`
- `CMD_UPDATE_INVISIBLE_STATE`
- `CMD_UPDATE_MONSTER_TYPE`
- `CMD_SWITCH_SERVER`.

Interpretation:

This family describes AOI/world-object lifecycle, state sync, interaction and map transitions. Some are clearly update/event-side names; do not treat every `CMD_*` as a client request.

`LuaSystemAPI_Game.ClickNPC(npcID)` already gives a safer semantic NPC interaction path than fabricating a raw `CMD_CLICK_OBJECT` payload.

---

## 2. Movement / scene / actor actions

Vocabulary:

- `CMD_AUTO_PATH`
- `CMD_MOVE_TO_LOCATION`
- `CMD_DO_ACTION`
- `CMD_DO_LEAP`
- `CMD_MOVESPEED_CHANGED`
- `CMD_DRAG_TARGET`
- `CMD_ACTIVATE_TRAP`
- `CMD_PLAY_SOUND`
- `CMD_PLAY_TEMPORARY_FX`
- `CMD_SYNS_STATE` (spelling preserved).

Preferred automation layer:

- `Game.GoTo`
- `Game.MoveTo`
- `Game.HasPath`
- `Game.ChaseTarget`
- `Game.DoAction`

before considering raw packet replay.

---

## 3. Inventory / item / economy

Vocabulary:

- `CMD_UPDATE_MONEY`
- `CMD_ADD_ITEM`
- `CMD_UPDATE_ITEM`
- `CMD_SWAP_ITEMS`
- `CMD_REMOVE_ITEM`
- `CMD_UPDATE_ITEMS_LIST`
- `CMD_ITEM_PACK`
- `CMD_UPDATE_TRADER_STATE`
- `CMD_STALL_ACTION`.

Observed inbound/update processors include:

- `ProcessRemoveItem`
- `ProcessUpdateItemsList`
- `ProcessUpdateMoney`
- `ProcessUpdateTraderState`.

### Exact request contracts already solved

#### Item action

`CMD_ITEM_ACTION = 100005`

Verified observed payload families:

- Equip -> `1:instanceID`
- Use -> `3:instanceID`
- Abandon -> `4:instanceID`
- Move -> `5:instanceID:destinationSite`
- Split -> `8:instanceID:quantity`.

#### Bag/site sort

`CMD_BAG_SORT = 100006`

Bag payload:

`10`

Storage sorting uses the target storage site.

#### NPC shop sell

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

Payload:

`itemInstanceID:NpcShopID:ShopID`

This uses the **live item instance ID**, not template ItemID.

#### NPC shop data

`CMD_NPC_SHOP_DATA = 200034`

Verified as server/shop data lifecycle used to open/refresh the NPC shop UI. Do not send it as if it were the sell request.

### Mutation rule

For item/shop actions:

`one current instance -> one request -> wait Remove/UpdateItemsList/money/shop proof -> fresh rescan`.

Never call `Process*` handlers as fake requests.

---

## 4. Skill / combat

Vocabulary:

- `CMD_ADD_SKILL`
- `CMD_REMOVE_SKILL`
- `CMD_REFRESH__GROUP_SKILLS_LIST` (spelling preserved)
- `CMD_REFRESH_SKILLS_CD`
- `CMD_USE_SKILL`
- `CMD_NEW_MISSILE`
- `CMD_NEW_SKILL_EXPLODE`
- `CMD_SKILL_DAMAGE`
- `CMD_SKILL_HEAL`
- `CMD_PUPPET_ATTACK`.

For automation, prefer semantic skill APIs already proven by shipped UI:

- `Game.UseSkill(skillID)`
- `Game.RequestUsingSkillWithTarget`
- `Game.RequestUsingSkillWithPos`
- `Game.CanUseSkill`
- `Game.GetSkillCooldown`.

Packet/event vocabulary is especially useful for **observation/telemetry**, not as the first action layer.

---

## 5. Buff / status

Vocabulary:

- `CMD_ADD_BUFF`
- `CMD_UPDATE_BUFF`
- `CMD_REMOVE_BUFF`.

Runtime semantic state is already stronger than the old command-name-only inference:

- `Game.GetBuffs()` -> BuffID, DurationTick, Stack;
- `Game.GetBuffData(BuffID)`;
- `Game.GetBuffProperties(BuffID)`;
- add/update/remove events drive UI state.

Do not infer a “cast buff” request from an inbound `CMD_ADD_BUFF`; actual buff application normally results from skill use/server authority.

---

## 6. Task / quest

Vocabulary:

- `CMD_ASSIGN_TASK`
- `CMD_COMPLETE_TASK`
- `CMD_UPDATE_TASK`
- `CMD_ABANDON_TASK`
- `CMD_UPDATE_NPC_TASK_STATE`.

The earlier prediction “task config probably exists” is obsolete: **`Tasks.xml` is VERIFIED with 516 rows**, and built-in Auto Quest consumes structured task data.

Canonical docs:

- `analysis/23_TASK_QUEST_AUTOMATION.md`
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

Task update events are state evidence; objective actions still depend on task type/NPC/monster/item/area semantics.

---

## 7. Pet / Spirit / summon

Vocabulary includes:

- `CMD_ADD_PET`
- `CMD_UPDATE_PET`
- `CMD_REMOVE_PET`
- `CMD_GET_PET`
- `CMD_TOGGLE_RIDE`
- `CMD_UPDATE_PET_TITLE`
- `CMD_ADD_SPIRIT`
- `CMD_UPDATE_SPIRIT`
- `CMD_REMOVE_SPIRIT`
- `CMD_GET_SPIRIT`
- `CMD_SPIRIT_UPDATE_POSITION`
- `CMD_PUPPET_ATTACK`.

Exact Pet/Spirit runtime/action evidence is documented in `analysis/24_PET_SPIRIT_AUTO_RUNTIME.md`.

Static Config also contains:

- `Pets` 8,349 rows;
- `PetFeatures` 11;
- `PetEquips` 70;
- `PetEquipSets` 13;
- `Spirits` 1,889;
- `SpiritFeatures` 3.

---

## 8. Appearance / fashion / mounts

Vocabulary:

- `CMD_APPEARANCE_ACTION`
- `CMD_OTHER_UPDATE_EQUIP`
- `CMD_TOGGLE_ACTIVE_FASHION`
- `CMD_WING_ACTION`
- `CMD_TOGGLE_ACTIVE_WEAPON_VISUAL`
- `CMD_SET_WEAPON_VISUAL`
- `CMD_FASHION_ORNAMENT_ACTION`
- `CMD_DOUBLE_RIDE`
- `CMD_PUBLIC_MOUNT`
- `CMD_SHAPE_SHIFTING_ACTION`
- `CMD_UPDATE_ROLE_ANIMATED_TITLE`.

Useful mainly for appearance-state observation/inspection. Lower priority for core Train/Buff/Sell.

---

## 9. Team / allies / group

Vocabulary includes:

- `CMD_UPDATE_TEAMDATA`
- guild/team notification families
- `CMD_ALLIES_NOTIFY`
- `CMD_ALLIES_SYSN_DATA` (spelling preserved)
- `CMD_ALLIES_UPDATE_MEMBER`
- `CMD_UPDATE_GROUP_NOTIFY`.

The old “team data may be available” prediction is now partly solved:

- global `C_TeamData` exists;
- member RoleID/RoleName/Level/FactionID/MapID/Hp/MaxHp/AvartaID/PosX/PosY are VERIFIED;
- `C_TeamAction` action values/payloads are documented in `analysis/25_TEAM_RUNTIME_FOLLOW.md`.

Use semantic team state/action evidence there instead of rediscovering from command names.

---

## 10. Revive / reincarnation

Exact action is solved:

`CMD_REVIVE_DATA = 200063`

Revive type values:

- normal / Đầu thai = `1`
- newbie = `2`
- skill revive = `3`.

This supersedes generic speculation around `CMD_REVIVE` names.

Canonical source: `features/AUTO_REVIVE.md` / `research/VERIFIED_PHASE2.md`.

---

## 11. Dynamic NPC dialog

Exact semantic contract:

`CMD_SHOW_GAMEDIALOG = 100007`

Payload:

`selectionID:SelectedItemID`

Active server data maps:

`Selections[selectionID] = visibleText`.

Do not invent a global treatment selection ID.

---

## 12. Faction / PK / reputation / title

Vocabulary:

- `CMD_UPDATE_FACTION`
- `CMD_PK_VALUE`
- `CMD_REPUTE_ACTION`
- `CMD_TITLE_ACTION`
- `CMD_CHANGE_CURRENT_TITLE`
- title/name update commands.

Static Config now also provides faction/reputation/title tables, so use both layers:

- runtime events for current state;
- Config for ID/template interpretation.

---

## 13. Chat / Captcha / Lua / voice

Vocabulary:

- `CMD_CHAT_DATA`
- `CMD_CAPTCHA`
- `CMD_CLIENT_LUA`
- `CMD_VOICE_CHAT`
- `CMD_VOICE_REALTIME`.

Known:

- Captcha is explicit UI/manual-verification state; automation must pause rather than solve/bypass.
- realtime voice aligns with LiveKit backend/module.
- `CMD_CLIENT_LUA` remains unresolved in direction/payload/use and stays a targeted hypothesis only.

---

## 14. Progress / gather / crafting-like state

Vocabulary includes:

- `CMD_UPDATE_GATHER_MAKE_POINT`
- progress begin/update/interruption events/processors.

Progress lifecycle is now VERIFIED event-driven (`BeginProgress`, `InteruptProgress`, `UpdateProgressTime`), so state machines should observe it rather than sleep blindly.

`GrowPoints` static Config has 407 gather/life-skill/quest rows for template interpretation.

---

## 15. Dungeon / FuBen exact packet family

From `TCPPacketDefine`, high-value verified IDs include:

- `CMD_FUBEN_AUTO_DATA = 200168`
- `CMD_FUBEN_KILL_PROGRESS = 200169`
- `CMD_FUBEN_QUERY_ALIVE = 200170`
- `CMD_FUBEN_MATCHMAKING = 200171`
- `CMD_FUBEN_COMPLETE = 200173`
- `CMD_FUBEN_SYNC_TARGET = 200174`.

Existence/ID is VERIFIED. Payloads/directions must still come from actual Lua handlers/request code before replay.

Static `FuBenScenarios` has 19 scenario definitions.

---

## 16. Network observer architecture

Recommended observation model:

```text
Inbound/outbound observation
 -> classify packet/event
 -> extract semantic IDs/state
 -> immutable Event
 -> Snapshot Store
 -> State Machine reacts
```

Do not mutate gameplay state inside a packet hook.

Useful future telemetry targets:

- skill damage/heal;
- death;
- buff lifecycle;
- loot/item updates;
- team/task changes;
- map transitions.

---

## 17. Evidence levels for network data

### Level A — symbol only

Example: metadata string `CMD_CLIENT_LUA`.

Known: name exists.

Unknown: ID/direction/payload unless cross-linked elsewhere.

### Level B — exact packet constant

Example: entry in `TCPPacketDefine` / `PACKET_IDS.csv`.

Known: symbol + numeric ID.

Still unknown: direction/payload unless traced.

### Level C — exact legitimate request construction

Example:

`CMD_NPC_SHOP_SELL_REQUEST = 200036`

`itemInstanceID:NpcShopID:ShopID`.

This is safe to document as an exact request contract for the frozen client.

### Level D — request + response/state lifecycle

Example Auto Sell:

request -> RemoveItem/UpdateItemsList/money/shop state -> fresh bag scan.

This is the preferred level for building a reliable state machine.

---

## 18. What this catalog is for

Use it to avoid rediscovering protocol vocabulary and to know which network paths are already solved.

For exact numeric lookup use `database/PACKET_IDS.csv`.

For exact verified action payloads use:

- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`
- subsystem docs such as `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`, `analysis/25_TEAM_RUNTIME_FOLLOW.md`, `analysis/26_STORAGE_BANK_ITEM_MOVE.md`.

Do not broad-reverse network code if the required contract is already present there.
