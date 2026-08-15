# PROBABLE findings

> Các mục ở đây có bằng chứng mạnh nhưng chưa đủ để coi là runtime-verified end-to-end. AI được phép dùng chúng để định hướng, nhưng phải giữ nhãn PROBABLE khi đưa vào implementation.

## 1. `LuaSystemSharedData` là query layer chính cho world scanner

**Confidence: HIGH**

Evidence:

- có `GetNearbySprites`, `GetNearbyObjects`, `GetLocalMapObjects`, `GetNearByEnemies`, `GetNearByPeacePlayers`, `GetNearestNPC`, item-pack queries;
- closures gần đó nhắc `npcData`, `monsterData`, `petData`, `portalData`, `zoneData`.

Prediction:

Có thể lấy danh sách nearby world objects qua API/data layer này thay vì heap-scan toàn process.

Cần verify:

- instance/static access;
- return types và fields cụ thể.

## 2. Nearby player/entity object chứa nhiều state hơn HP

**Confidence: HIGH**

Runtime trước đó đã quan sát Name/RoleID/HP/MaxHP/position của player trong phạm vi client. Network/world architecture còn có faction/team/PK/combat/death/target/buff state.

Prediction:

Cùng object hoặc related data có thể cung cấp:

- MP/MaxMP;
- level/class/faction;
- TeamID;
- PK/combat state;
- target;
- death/moving state;
- appearance/title/guild;
- buff reference/list.

Không được giả định exact offsets.

## 3. Config.unity3d chứa static game database quan trọng

**Confidence: HIGH**

Evidence:

- tên file `Config.unity3d`;
- GameAssembly lộ rất nhiều template/data APIs và `NPCData`, `MonsterData`, `PortalData`, item/skill/magic keys;
- game có custom asset decrypt DLL.

Prediction:

Sau decrypt/extract sẽ tìm được ít nhất một phần của:

- NPC/map/monster;
- item/equipment/gem;
- skill/buff/magic;
- quest/task;
- portal/zone.

Exact table/file names chưa known.

## 4. Interface.unity3d chứa Lua/UI definitions cần cho NPC/shop/auto

**Confidence: HIGH**

Evidence:

- `LuaSystemManager.LoadFromAssetBundle`;
- high-level Lua GUI APIs;
- bundle tên Interface + Shared/LoadingResources;
- callback cụ thể không xuất hiện như public C# helper.

Prediction:

Exact UI script names/callbacks cho Trị liệu, shop, Đầu thai, Auto/Đánh quái có khả năng nằm ở interface/Lua asset layer.

## 5. Built-in Auto Fight có state/radius riêng

**Confidence: MEDIUM-HIGH**

Evidence:

- `get/set_EnableAutoF1`;
- `RangerAuto`, `RangerRequest`, auto flags;
- `DrawCicleAutoFight`;
- `RemoveAutoFightMark`.

Prediction:

UI “Auto -> Đánh quái” có thể đang cấu hình một built-in auto subsystem, không phải chỉ bật một button callback đơn giản.

Cần trace manual toggle để biết exact Lua action/config.

## 6. NPC action nên đi qua `ClickNPC` thay vì mouse click

**Confidence: VERY HIGH**

Disassembly của `ClickNPC` đã cho thấy stop-path -> locate -> face/select -> `SendClickOnObject`.

Prediction:

Đây là entry point ổn định hơn coordinate click cho mở NPC. End-to-end vẫn cần main-thread/state validation.

## 7. Shop action là Lua callback -> packet -> server update

**Confidence: HIGH**

Evidence:

- không thấy helper C# rõ kiểu SellItem;
- GUI/Lua/network bridge hiện diện;
- ProcessRemoveItem/UpdateItemsList/UpdateMoney/TraderState hiện diện.

Prediction:

Một trace manual sell sẽ lộ callback/packet đủ để replay chuẩn.

## 8. Treatment/Heal NPC cũng là Lua callback/network flow

**Confidence: HIGH**

Evidence tương tự shop: ClickNPC mở interaction, nhưng treatment helper C# rõ ràng chưa thấy; Lua GUI + SendPacket bridge có sẵn.

Prediction:

Trace `CallUI/MainCallUI + SendPacket` khi bấm Trị liệu/Đồng ý sẽ cho exact action sequence.

## 9. Asset custom transform chủ yếu là obfuscation

**Confidence: HIGH**

FGClientTool decrypt dùng swap/add/sub/xorshift + header checks `UnityFS/UnityRaw/UnityWeb`, không giống cipher cryptographic mạnh.

Prediction:

Port exact native algorithm sẽ phục hồi bundle để standard Unity extractor xử lý.

## 10. Launcher có multi-process/sync/record-playback layer riêng

**Confidence: HIGH**

Binary strings trực tiếp có session/process IDs, sync group/master, recording/playback process/group methods.

Prediction:

Có thể nghiên cứu launcher để tái sử dụng process/session orchestration, nhưng per-game runtime data vẫn phải tách context từng process.

## 11. Buff-aware auto buff khả thi

**Confidence: MEDIUM-HIGH**

`GetBuffs`, `HasBuff`, `GetBuffData`, target buff icons tồn tại.

Prediction:

Khi map return object, auto buff có thể quyết định theo buff ID/duration/stack + HP policy, không chỉ HP%.

## 12. Ground-loot scanner khả thi

**Confidence: HIGH**

`GetNearestItemPack`, `GetNearbyItemPack`, `PickUpItemFromItemPack` tồn tại.

Prediction:

Có thể enumerate ItemPack ID/distance và pick up semantic items sau khi map exact pack data.

## 13. NPC/map offline DB có thể tự sinh

**Confidence: MEDIUM-HIGH**

`GetNearestNPC(npcResID)`, `NPCData`, `PortalData`, `ZoneData` + config bundles.

Prediction:

Có thể sinh Map -> NPC RESID -> Name -> X/Y -> service relationship, thay vì nhập tay từng NPC.
