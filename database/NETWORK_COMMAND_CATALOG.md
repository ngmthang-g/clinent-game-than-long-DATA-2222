# Network Command / Event Catalog

> Các tên dưới đây được lấy từ metadata/string evidence của snapshot. **Tên tồn tại là VERIFIED; direction, numeric ID và payload KHÔNG được tự suy ra nếu chưa trace callsite.**

## 1. Core world/object lifecycle

| Command/name | Diễn giải có khả năng |
|---|---|
| `CMD_CHANGE_MAP` | chuyển map / map transition |
| `CMD_NEW_OBJECTS` | server/client báo các object mới vào phạm vi |
| `CMD_REMOVE_OBJECTS` | loại object khỏi local world/AOI |
| `CMD_OBJECT_LOAD_ALREADY` | object finished/ready state |
| `CMD_CLICK_OBJECT` | interaction/click object request/event |
| `CMD_OBJECT_DEATH` | object death state/event |
| `CMD_REVIVE` | revive/rebirth related request/event |
| `CMD_SYNC_DATA` | sync main object/player data |
| `CMD_OTHER_SYNC_DATA` | sync data cho object khác |
| `CMD_UPDATE_OBJECT_TITLE` | object title update |
| `CMD_UPDATE_NAME` | name update |
| `CMD_UPDATE_INVISIBLE_STATE` | invisibility state update |
| `CMD_UPDATE_MONSTER_TYPE` | monster type/state change |
| `CMD_SWITCH_SERVER` | server switch/transition |

## 2. Movement / action / scene

| Command/name | Diễn giải có khả năng |
|---|---|
| `CMD_AUTO_PATH` | auto path request/state |
| `CMD_MOVE_TO_LOCATION` | move-to position |
| `CMD_DO_ACTION` | generic actor action |
| `CMD_DO_LEAP` | leap movement/action |
| `CMD_MOVESPEED_CHANGED` | movement speed update |
| `CMD_DRAG_TARGET` | forced drag/pull target |
| `CMD_ACTIVATE_TRAP` | trap activation |
| `CMD_PLAY_SOUND` | play sound event |
| `CMD_PLAY_TEMPORARY_FX` | temporary visual effect |
| `CMD_SYNS_STATE` | state synchronization string as present in binary (spelling preserved) |

Related processors/strings include object position change, dynamic obstruction label updates, progress state and scene sync.

## 3. Inventory / item / economy

| Command/name | Diễn giải có khả năng |
|---|---|
| `CMD_UPDATE_MONEY` | money/currency update |
| `CMD_ADD_ITEM` | add item instance |
| `CMD_UPDATE_ITEM` | item instance update |
| `CMD_SWAP_ITEMS` | swap/move item slots |
| `CMD_REMOVE_ITEM` | remove item instance |
| `CMD_UPDATE_ITEMS_LIST` | replace/refresh item collection |
| `CMD_ITEM_PACK` | ground item pack / loot pack related |
| `CMD_UPDATE_TRADER_STATE` | trader/shop state update |
| `CMD_STALL_ACTION` | stall/player-shop style action |

Known inbound processor names:

- `ProcessRemoveItem`
- `ProcessUpdateItemsList`
- `ProcessUpdateMoney`
- `ProcessUpdateTraderState`

### Safety note

Các `Process*` rất có khả năng là **response/update handlers**. Không gọi chúng để giả lập request bán/mua.

## 4. Skill / combat

| Command/name | Diễn giải có khả năng |
|---|---|
| `CMD_ADD_SKILL` | add/unlock skill |
| `CMD_REMOVE_SKILL` | remove skill |
| `CMD_REFRESH__GROUP_SKILLS_LIST` | refresh grouped skill list (spelling preserved) |
| `CMD_REFRESH_SKILLS_CD` | refresh cooldowns |
| `CMD_USE_SKILL` | skill use request/event |
| `CMD_NEW_MISSILE` | projectile/missile spawn |
| `CMD_NEW_SKILL_EXPLODE` | skill explosion/AOE event |
| `CMD_SKILL_DAMAGE` | damage result/event |
| `CMD_SKILL_HEAL` | heal result/event |
| `CMD_PUPPET_ATTACK` | puppet/summon attack |

Potential use for combat recorder: correlate use-skill -> damage/heal -> death/buff events by timestamp and target identifiers.

## 5. Buff / status effects

| Command/name | Diễn giải có khả năng |
|---|---|
| `CMD_ADD_BUFF` | new buff/status |
| `CMD_UPDATE_BUFF` | buff stack/duration/property update |
| `CMD_REMOVE_BUFF` | remove buff/status |

Related Lua events include AddBuff/UpdateBuff semantics. Exact payload fields still need runtime schema mapping.

## 6. Task / quest

- `CMD_ASSIGN_TASK`
- `CMD_COMPLETE_TASK`
- `CMD_UPDATE_TASK`
- `CMD_ABANDON_TASK`
- `CMD_UPDATE_NPC_TASK_STATE`

### Prediction

Có task/quest model đủ để theo dõi quest ID/progress/NPC state. Static quest config có khả năng nằm trong Config bundle.

## 7. Pet / spirit / puppet

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
- `CMD_PUPPET_ATTACK`

## 8. Appearance / fashion / mount

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
- `CMD_UPDATE_ROLE_ANIMATED_TITLE`

Useful if future scanner needs appearance/equipment state of nearby players.

## 9. Team / allies / group

Known names include:

- `CMD_UPDATE_TEAMDATA`
- guild/team notify family
- `CMD_ALLIES_NOTIFY`
- `CMD_ALLIES_SYSN_DATA` (spelling preserved)
- `CMD_ALLIES_UPDATE_MEMBER`
- `CMD_UPDATE_GROUP_NOTIFY`

### Prediction

Team/ally state may be available both via network updates and `LuaSystemSharedData` queries.

## 10. Faction / PK / reputation / title

- `CMD_UPDATE_FACTION`
- `CMD_PK_VALUE`
- `CMD_REPUTE_ACTION`
- `CMD_TITLE_ACTION`
- `CMD_CHANGE_CURRENT_TITLE`
- object title/name update commands.

Potential fields for entity scanner: faction, PK value, current title, reputation-related state.

## 11. Chat / captcha / Lua / voice

- `CMD_CHAT_DATA`
- `CMD_CAPTCHA`
- `CMD_CLIENT_LUA`
- `CMD_VOICE_CHAT`
- `CMD_VOICE_REALTIME`

`CMD_VOICE_REALTIME` aligns with `Version.xml` LiveKit backend and `livekit_ffi.dll`.

`CMD_CLIENT_LUA` is especially interesting but direction/payload unknown. Do not experiment by fabricating payload; trace a legitimate action if needed.

## 12. Progress / gather / crafting-like state

Strings/commands include progress handling and:

- `CMD_UPDATE_GATHER_MAKE_POINT`
- progress begin/update/interruption-related processors/events.

Potential use: detect channeling/gathering/crafting state instead of fixed delays.

## 13. Network event observer architecture

Recommended observer model:

```text
Raw inbound/outbound observation
 -> classify by command/processor
 -> extract semantic IDs/state
 -> publish immutable Event
 -> Snapshot Store updates
 -> State Machine reacts
```

Do **not** make action logic mutate game state inside a packet hook. Hooks should observe/log and hand off.

## 14. High-value traces for unresolved features

### Sell

Capture:

```text
manual sell 1 item
 -> outgoing SendPacket
 -> command/payload
 -> ProcessRemoveItem
 -> ProcessUpdateMoney
 -> ProcessUpdateItemsList
 -> optional trader-state update
```

### Revive

```text
dead UI action
 -> outgoing request
 -> CMD_REVIVE related flow
 -> object/map/spawn state
```

### Auto combat

Observe UI callback and state change; do not assume `CMD_USE_SKILL` itself represents turning auto mode on.

## 15. What this catalog does NOT provide

- numeric command IDs;
- protobuf/message schemas;
- direction for every name;
- server authorization rules;
- safe replay payloads.

Those are targeted trace tasks only. The purpose of this file is to stop future AI from rediscovering the command vocabulary and subsystem grouping.
