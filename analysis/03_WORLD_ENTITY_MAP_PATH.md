# World / Entity / Map / Pathfinding

## 1. Kết luận quan trọng

Client có bằng chứng cụ thể về một lớp query dữ liệu thế giới (`LuaSystemSharedData`) và một lớp scene/game-object (`FGStudio.Engine.Objects.GScene`). Vì vậy hướng mạnh nhất là **đi từ các query/game structures đã tồn tại**, không phải scan RAM toàn bộ để tìm từng entity bằng heuristic.

## 2. LuaSystemSharedData — world query layer

Các method/string đã thấy:

- `GetNearestNPC(npcResID)`
- `GetNearbySprites(includeDeath)`
- `GetNearbyTeamLeaders`
- `GetNearTeammates(includeNonePlayers, lowHPPriority, maxTargets)`
- `GetNearByEnemyIDs`
- `GetNearByEnemies`
- `GetNearByPeacePlayers`
- `GetNearbyObjects`
- `GetLocalMapObjects`
- `GetNearestItemPack`
- `GetNearbyItemPack`

Compiler-generated closures/lambdas gần subsystem này nhắc tới:

- `npcData`
- `monsterData`
- `petData`
- `markData`
- `growPointData`
- `portalData`
- `zoneData`

### Diễn giải

Khả năng cao game đã chuẩn hóa các object trong phạm vi client biết thành các data object mà Lua có thể query. Đây là entry point ưu tiên cho:

- nearby player list;
- NPC scanner;
- monster/boss scanner;
- pet/object/item-pack scanner;
- portal/zone lookup;
- target filtering.

Không cần giả định tồn tại class đúng tên `EntityManager`; bằng chứng hiện tại mạnh hơn nằm ở `LuaSystemSharedData`.

## 3. GScene

Đã thấy class `GScene` dưới namespace `FGStudio.Engine.Objects` cùng các member/string như:

- `GetGroundHeight`
- `InSafeArea`
- `CanEnter`
- `ScreenToPosition`
- `ShowSelectTargetDecoration`
- `HideSelectTargetDecoration`
- `DoSyncPosition`
- `DoVisionLogic`
- `DoCheckPetLogic`
- `LoadDecoBot`
- `get_PathFinder`
- `LoadRoleWeapon`
- `LoadRoleSoul`
- `LoadRoleWings`
- `LoadRoleFashionOrnaments`
- `LoadRoleModel`
- `LoadLeader`
- `LoadOtherRole`
- `LoadTrap`

### Ý nghĩa

`GScene` không chỉ là renderer. Tên method cho thấy nó tham gia:

- scene object loading;
- target decoration;
- position synchronization;
- vision/AOI-style logic;
- pet checking;
- safe-area/enterability;
- pathfinder access.

`ClickNPC` đã được disassemble thấy gọi `GScene.SelectTarget`, củng cố vai trò trung tâm của scene/selection system.

## 4. Pathfinding / map components

Các symbol/string liên quan:

- `PathFinder`
- `NodeGrid`
- `LocalMapComponents`
- `Obstructions`
- `DynamicObstructions`
- `Regions`
- `SafeAreas`
- `gridX`
- `gridY`
- `InDynamicObs`
- `zones`
- dynamic obstruction labels

Các data classes gần đó:

- `NPCData`
- `MonsterData`
- `GrowPointData`
- `ZoneData`
- `PortalData`
- `MapAreaSoundData`

### Hướng ứng dụng

Có cơ sở mạnh để nghiên cứu:

- current map -> local objects;
- map cell/grid -> world distance;
- obstacle-safe movement;
- map NPC/portal DB;
- train spot -> vendor NPC -> return path;
- portal chain giữa map.

Nhưng chưa được phép khẳng định toàn bộ NavMesh/route graph đã có sẵn ở dạng dễ đọc; cần inspect data cụ thể trong `PathFinder/NodeGrid` hoặc asset bundle.

## 5. Target/movement API liên quan

Trong `LuaSystemAPI_Game` có:

- `SelectTarget`
- `ClickToObject`
- `ClickNPC`
- `ChaseTarget`
- `get_CurrentChaseTargetID`
- `IsSelectTargetDie`
- `IsAllowDeadTarget`
- `StopAutoPath`
- `HasPath`
- `CanMove`
- `IsMoving`
- `GetDistance`
- `CalculatePointOnLine`
- `CellToDistance`
- strings/lambdas quanh `MoveToEx`, `GoTo`.

Điều này cho thấy movement/target layer của game có API semantic khá cao. Không nên mặc định phải gửi phím/WASD/mouse.

## 6. AOI — giới hạn dữ liệu cần nhớ

Việc client thấy HP/MaxHP người khác không cùng tổ đội chứng minh **server có replicate entity state trong phạm vi quan sát**. Nó không chứng minh client biết toàn bộ người trên toàn map.

Mô hình đúng:

```text
Server world
 -> AOI/visibility replication
 -> client-side entity/object structures
 -> LuaSystemSharedData/GScene/query layer
```

Do đó scanner chỉ có thể đọc object đã được server/client load. Một player rất xa, chưa được replicate, sẽ không tự nhiên tồn tại trong RAM để đọc.

## 7. Những field/state có khả năng nằm cùng entity hoặc related data

### Đã có quan sát runtime trước đó

- Name
- RoleID
- HP
- MaxHP
- Position

### PROBABLE dựa trên architecture/network/data names

- MP/MaxMP
- faction/class
- level
- TeamID
- PK state/value
- combat state
- current target
- movement/death state
- buff/debuff list hoặc reference
- current skill/action/animation state
- guild/title/appearance info

Các mục PROBABLE không được coi là field layout đã biết. AI sau này nên query object/type metadata hoặc SharedData output thay vì đoán offset.

## 8. NPC database và RESID

`GetNearestNPC(npcResID)` là bằng chứng trực tiếp rằng NPC có một identifier kiểu resource ID dùng cho query. `NPCData` và config bundles tạo nền tảng cho database:

```text
MapID
 -> NPC RESID / object/template ID
 -> Name
 -> Position
 -> role/service flags (nếu config có)
```

Dự đoán mạnh: `Config.unity3d` hoặc data bundle chứa bảng tĩnh để map RESID -> tên/toạ độ/service. Nhưng chưa được đánh dấu VERIFIED cho tới khi bundle được extract và bảng cụ thể được đọc.

## 9. Monster/boss scanner

Bằng chứng `MonsterData`, nearby sprites/enemies và network object add/remove/death đủ để đánh giá khả năng rất cao:

- phân biệt monster từ nearby object;
- đọc object/template ID;
- HP/MaxHP nếu replicated;
- position/distance;
- alive/dead;
- current target/combat state ở mức nào đó.

Ứng dụng:

- chọn mob thật thay vì pixel;
- tránh target đã chết;
- boss spawn detector trong AOI;
- theo dõi boss HP.

## 10. Ground item / ItemPack

`GetNearestItemPack`, `GetNearbyItemPack` và `PickUpItemFromItemPack(itemPackID, slotIndex, UsingAuto)` là bằng chứng mạnh rằng loot trên đất có representation semantic, không chỉ visual object.

Có thể xây:

```text
NearbyItemPack
 -> ItemPackID
 -> distance/position
 -> slots/items (cần map exact data)
 -> pickup action
```

Exact fields của ItemPack chưa được dump đầy đủ trong KB này.

## 11. State machine nên dựa vào world state

Ví dụ revive/train flow:

```text
Alive
 -> Dead
 -> Revive UI available
 -> action
 -> Loading/ChangeMap
 -> Spawned
 -> CurrentMap valid
 -> Position valid
 -> return to train point
 -> enable combat
```

Không dùng delay 6 giây như logic chính. Delay chỉ nên là timeout/fallback.

## 12. Mục tiêu targeted research nếu cần exact implementation

Ưu tiên theo thứ tự:

1. Resolve `LuaSystemSharedData` instance/static methods.
2. Dump return object types của `GetNearbySprites`, `GetNearbyObjects`, `GetLocalMapObjects`.
3. Map `NPCData`, `MonsterData`, `PortalData` fields.
4. Resolve `GScene` current instance/static access.
5. Inspect `PathFinder`/`NodeGrid` data only khi cần route chính xác.

Không cần reverse toàn bộ UnityPlayer hoặc toàn bộ GameAssembly lại.
