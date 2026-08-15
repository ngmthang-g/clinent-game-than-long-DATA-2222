# PROBABLE findings — remaining after Phase 2

> Phase 2 đã nâng nhiều giả thuyết cũ thành VERIFIED. File này chỉ giữ các kết luận còn có bằng chứng mạnh nhưng chưa đủ end-to-end/runtime proof.

## 1. `LuaSystemSharedData` là query layer chính cho runtime world scanner

**Confidence: VERY HIGH**

Evidence:
- `GetNearbySprites`, `GetNearbyObjects`, `GetLocalMapObjects`, `GetNearByEnemies`, `GetNearByPeacePlayers`, `GetNearestNPC`, item-pack queries tồn tại;
- built-in Auto Fight thực tế dùng nearby-sprite APIs để tìm quái.

Prediction:
- external read-only scanner có thể lấy world entities từ semantic query/data layer thay vì heap-scan toàn process.

Chưa VERIFIED:
- exact return type của từng API;
- full field schema cho Player/NPC/Monster/Pet/Object.

## 2. Nearby player/entity object chứa nhiều state hơn HP/position

**Confidence: HIGH**

Runtime cũ đã quan sát Name/RoleID/HP/MaxHP/position của player trong AOI. Engine/API/network vocabulary cho thấy faction/team/combat/death/target/buff concepts tồn tại.

Likely fields hoặc related objects:
- MP/MaxMP;
- level/faction/class;
- TeamID;
- combat/PK/death/moving state;
- target;
- guild/title/appearance;
- buff list/reference.

Không được giả định offsets cho đến khi return object schema được map.

## 3. `LangZhong1/2` là dấu hiệu rất mạnh của NPC y sư/trị liệu

**Confidence: HIGH, nhưng service contract chưa runtime-confirmed**

Evidence:
- nhiều NPC có tên mang nghĩa y/dược dùng `ResName=LangZhong1/2`;
- Lâu Lan có ba NPC liên tiếp 337/338/339 dùng `LangZhong1`, trong đó 339 là Đỗ Thanh Đằng;
- Config còn có NPC 912 `Tháp trị liệu`, ResName `ZhiLiaoTa`.

Prediction:
- ResName family có thể dùng làm **candidate classifier** để tìm healer service NPC.

Chưa VERIFIED:
- mỗi NPC `LangZhong*` có cùng menu/service hay không;
- selection text/ID cụ thể mà server trả ở từng map/state.

## 4. NPC Trị liệu nên được chọn bằng active `GameDialog.Selections`

**Confidence: VERY HIGH**

Evidence:
- generic NPC dialog is server-driven;
- selectionID được gắn vào visible text;
- built-in FuBen auto đã có exact pattern lowercase/text-match rồi gửi actual selection ID.

Prediction:
- treatment flow có thể ổn định bằng semantic text matching (`Trị liệu`, hoặc text tương đương do server trả) thay vì hardcode button pointer/selection ID.

Cần runtime proof trên đúng NPC mong muốn và xác nhận outcome HP/money/dialog state.

## 5. Buff-aware auto buff có thể dùng object buff data thay vì suy luận HP đơn thuần

**Confidence: HIGH**

Evidence: `GetBuffs`, `HasBuff`, `GetBuffData`, `GetBuffProperties`, target buff icons tồn tại.

Prediction:
- sau khi map return schema có thể quyết định theo buff ID/duration/stack/source/target kết hợp HP policy.

## 6. Ground-loot scanner có thể đọc semantic item-pack object

**Confidence: HIGH**

Evidence: built-in Auto Fight dùng `GetNearbyItemPack`, `GetNearestItemPack`, `PickUpItemFromItemPack`.

Prediction:
- có thể enumerate drop package ID/position/distance/contents đủ để lọc loot tốt hơn macro click.

Exact item-pack schema chưa map hoàn chỉnh.

## 7. Portal graph có thể dùng làm offline coarse-route planner

**Confidence: MEDIUM-HIGH**

Evidence:
- 165 portal edges có From/To map và tọa độ;
- built-in `Game.GoTo` đã hỗ trợ cross-map route abstraction.

Prediction:
- static graph có thể giúp chọn route/map topology, diagnostics hoặc fallback planning.

Caveat:
- portal có thể phụ thuộc level/quest/event/state;
- runtime `Game.GoTo` vẫn nên là route executor ưu tiên.

## 8. Một phần NPC service role có thể phân loại offline bằng Name/ResName

**Confidence: MEDIUM-HIGH**

Ví dụ semantic families như `LangZhong*`, `TieJiang`, `JiuDianLaoBan*`, `ShangRen`, `CaiFeng`, `YuFu` cho biết archetype/model và thường tương quan với nghề/service.

Prediction:
- có thể tạo candidate service tags để rút ngắn tìm kiếm NPC bán đồ/trị liệu/sửa đồ.

Không được coi ResName là API contract; phải validate dialog/shop data trước khi action.

## 9. External tool có thể gọi built-in AutoFight engine ổn định nếu dispatch đúng main thread/state

**Confidence: HIGH**

Lua semantics của engine đã rõ. Rủi ro còn lại là **bridge execution context** từ external tool vào Unity/Lua runtime.

Prediction:
- dùng resolver + proven Unity main-thread dispatcher + max-one-action queue sẽ ổn định hơn gọi native arbitrary thread hoặc click nền.

Cần implementation/runtime validation trên bridge hiện tại.
