# HYPOTHESES — giả thuyết cần kiểm chứng

> Đây là nơi cố ý lưu cả dự đoán để future AI có hướng đào, nhưng **không được nâng thành sự thật** nếu chưa có evidence mới.

## H1 — Có một object/data model chung cho Player/Monster/NPC/Pet

Evidence gián tiếp:

- nearby sprite/object queries;
- GScene load nhiều object type;
- shared world/network add/remove/death/movement events.

Giả thuyết:

Có base class/data hierarchy chung hoặc ít nhất interface/data shape chung cho world actors.

Cách test tốt nhất:

- inspect return types của `GetNearbySprites/GetNearbyObjects`;
- compare classes of player/NPC/monster runtime objects.

## H2 — HP/MaxHP của nearby players nằm trong role/sprite data object mà SharedData trả về

Evidence:

- đã quan sát realtime HP/MaxHP người ngoài team trong client RAM;
- query layer nearby player/sprite tồn tại.

Cần test:

- resolve field names/offsets từ actual return object;
- compare với known RoleID/Name/HP sample.

## H3 — `Config.unity3d` có bảng NPC service/type

Giả thuyết:

Ngoài NPC RESID/name/position, config có field để biết NPC làm vendor/healer/quest/teleport… hoặc reference tới service/dialog data.

Nếu đúng, auto có thể tự chọn NPC gần nhất theo dịch vụ thay vì hardcode Mã Kiêu Minh/Ba Nhĩ.

## H4 — `Interface.unity3d` chứa exact Lua function name cho shop/treatment/revive/auto

Có cơ sở mạnh nhưng chưa extract hoàn chỉnh. Tìm TextAsset/Lua payload/script registration sau decrypt.

## H5 — `CMD_CLIENT_LUA` được dùng cho một phần action/gameplay do Lua điều khiển

Tên command rất gợi ý client/server trao đổi payload Lua-specific. Chưa map callsites/payload.

Không gửi thử packet chỉ dựa trên tên; cần trace legitimate flow.

## H6 — Built-in Auto Fight lưu radius/center/return constraints

Evidence:

- `DrawCicleAutoFight`;
- Ranger/Auto flag methods.

Giả thuyết:

Auto subsystem có state như center point/radius/target policy. Nếu map được sẽ tốt hơn tự viết navigation loop từ đầu.

## H7 — Buff data có duration/stack/owner fields dễ đọc

Các magic keys có max stacks, timeout, group… và buff APIs tồn tại. Giả thuyết return data có đủ fields cho precise buff timer.

Cần inspect `GetBuffData/GetBuffProperties` actual type.

## H8 — Quest/task database nằm trong Config bundle

Network commands có assign/complete/update/abandon task; game chắc có task model. Chưa tìm table exact trong asset.

## H9 — Map path data có thể dùng offline

`PathFinder`, `NodeGrid`, obstruction/region/zone names cho thấy path model. Chưa biết graph/grid được load từ asset nào và có dễ serialize ra DB không.

Nếu đúng: có thể precompute/plan route NPC/portal/train offline.

## H10 — Launcher sync/record-playback có thể cung cấp official input/session orchestration

Launcher strings cho thấy sync group/master + recording/playback. Chưa xác định nó sync high-level commands, raw input hay một control service riêng.

Nếu nghiên cứu: decompile .NET Launcher trước, dễ hơn native reverse.

## H11 — `SyncBootstrap.AutoInit` liên quan launcher/client synchronization

Tên method đáng chú ý nhưng chỉ biết nó được runtime initialize. Có thể liên quan sync feature, cũng có thể chỉ là generic bootstrap. Không suy luận thêm nếu chưa decompile/method-map.

## H12 — Server sends enough combat state for a detailed combat recorder

Command names có skill damage/heal/death/buff. Giả thuyết payload đủ để thống kê damage/skill/target/timing. Crit flag và XP/loot linkage chưa được chứng minh.

## H13 — UI button object pointers bị recreate khi panel/script đổi

Đây là cơ chế rất phù hợp với lỗi stale `UIButton*`. Unity/Lua UI thường destroy/reinstantiate/rebind. Đã có binary evidence `HandleClickEvent` dereference instance; việc pointer thay đổi theo từng UI transition cần runtime object-ID logging để chứng minh trực tiếp.

## H14 — Một số static config/resource bundle được obfuscate bằng nhiều transform variants

FG_Decrypt có nhiều branch/phase và bundle headers hiện có mức biến đổi khác nhau. Có thể transform lựa chọn dựa trên file size/header/version.

## H15 — Có thể xây knowledge DB gần như hoàn chỉnh mà không cần giữ mọi pointer/offset

Kết hợp:

- metadata semantic names;
- Lua Game/SharedData queries;
- extracted static config;
- runtime observer.

Giả thuyết kiến trúc: phần lớn tool có thể dựa trên ID/data object semantic và chỉ dùng native pointer ở resolver/bridge nội bộ, giảm phụ thuộc offset rất nhiều.
