# Asset Bundles / Config / Interface / FGClientTool encryption

## 1. Vì sao asset branch quan trọng ngang GameAssembly

`GameAssembly.dll + global-metadata.dat` cho biết **logic và API**. Các `.unity3d` bundles có khả năng chứa **data cụ thể**: NPC/map/item/skill/UI/localization/config/resources. Muốn AI hiểu client mà không reverse lại, phải giữ hai nhánh tri thức song song.

## 2. Các bundle/data chính trong repo

### `data.unity3d`

- khoảng 47.6 MB;
- bắt đầu bằng header chuẩn `UnityFS`;
- version string quan sát: `6000.3.6f1`;
- ưu tiên cao vì là bundle lớn và không cần custom decrypt đầu vào.

### `StreamingAssets/Config.unity3d`

- khoảng 1.36 MB;
- header bị custom/obfuscate;
- ứng viên ưu tiên cao cho static configuration.

### `StreamingAssets/Interface.unity3d`

- khoảng 578 KB;
- header không phải `UnityFS` nguyên bản nhưng khi inspect binary vẫn lộ dấu liên quan `UnityFS`/CAB và version text `6000.3.7f1`;
- rất đáng đào cho UI/Lua script/resource mapping.

### `StreamingAssets/Interface/`

- `LoadingResources.unity3d`
- `Logo.unity3d`
- `Shared.unity3d`
- `Shared_2.unity3d`

Các file này có mức transform khác nhau; nhiều file có `CAB-...` markers sau header custom.

### `Translations.unity3d`

- khoảng 1.83 MB;
- ưu tiên trung bình/cao cho localization/text key mapping;
- có thể giúp nối UI labels/quest/item names với resource IDs sau khi extract.

### `Resources/unity default resources`

- built-in Unity resource data;
- có version string riêng (`6000.3.0b4` đã quan sát trong binary) nhưng **không được dùng để suy ra core game build**, vì default resources có thể đến từ engine/package build khác.

## 3. FGClientTool_Windows.dll

Native x64 DLL riêng của FGStudio. Export đã xác nhận:

- `FG_Decrypt`
- `FG_Encrypt`
- `HelloWorld`

`GameAssembly` có tham chiếu tới `FG_Encrypt`/`FG_Decrypt`, nên DLL này là thành phần thực, không phải file thừa.

## 4. FG_Encrypt — behavior đã disassemble

Behavior quan sát:

- nếu buffer null hoặc length không hợp lệ: bỏ qua/return;
- số pair xử lý tương đương `min(128, length / 2)`;
- thao tác trên byte ở đầu và cuối buffer;
- swap cặp front/back và cộng `0x0F` modulo 256 vào byte theo transform.

Exact pseudocode nên được lấy lại từ disassembly nếu port production, nhưng các đặc điểm trên đủ để nhận diện algorithm.

## 5. FG_Decrypt — behavior quan trọng

Disassembly cho thấy nhiều phase.

### Header detection

Hàm kiểm tra trực tiếp các signature:

- `UnityFS`
- `UnityRaw`
- `UnityWeb`

Nếu sau một phase transform header trở thành bundle Unity hợp lệ, hàm có đường return sớm.

### Custom transform branch

Một nhánh sử dụng length và constant:

`0x9E3779B9`

Sau đó dùng chuỗi xorshift kiểu:

```text
x ^= x << 13
x ^= x >> 17
x ^= x << 5
```

Từ `x` suy ra:

- số pair byte cần xử lý (bounded, tối đa vùng đầu/cuối);
- một byte delta/decrement custom;
- swap/adjust các byte front/back.

Điều này giải thích vì sao một số bundle trông random ở header nhưng vẫn lộ cấu trúc Unity/CAB phía sau.

## 6. Không nên gọi đây là “mã hóa mạnh”

Transform hiện thấy giống **custom obfuscation/header transformation** hơn cryptography hiện đại. Mục tiêu có vẻ là làm asset extractor tiêu chuẩn không nhận `UnityFS` ngay lập tức.

Vì vậy hướng đúng:

```text
read raw bundle
 -> reproduce FG_Decrypt exactly
 -> verify output starts UnityFS/UnityRaw/UnityWeb
 -> feed output to standard Unity bundle parser/extractor
```

Không cần brute force.

## 7. Mixed Unity version strings

Đã quan sát:

- `data.unity3d`: `6000.3.6f1`
- `Interface.unity3d`: text `6000.3.7f1`
- `unity default resources`: `6000.3.0b4`

Không nên kết luận mâu thuẫn. Bundle/resources có thể được build/repacked bằng minor editor/package versions khác nhau. Core client evidence hiện nghiêng về Unity 6 / 6000.3.x + IL2CPP x64.

## 8. Config.unity3d — predicted content

Dựa trên symbol/data class/magic keys trong GameAssembly, các nhóm data **có khả năng rất cao** tồn tại trong config/related bundle:

- NPC definitions / RESID / names / services;
- monster templates;
- map/zone/portal data;
- item templates/types/prices;
- equip/gem rules;
- skill/ability templates;
- buff/magic effect configuration;
- quests/tasks;
- visual/resource IDs.

Đây là PROBABLE, chưa phải verified table names trong bundle.

## 9. Interface bundles — predicted content

Dựa trên `LuaSystemManager.LoadFromAssetBundle`, `MainCallUI/FindUI`, UI classes và bundle name, có khả năng mạnh chứa:

- Lua UI scripts hoặc packaged script payload;
- UI prefab hierarchy;
- panel/button/resource names;
- shared UI assets;
- message boxes/loading UI;
- shop/NPC/auto-fight UI definitions.

Đây là nơi ưu tiên khi cần exact callback/name cho `Trị liệu`, `Bán nhanh`, `Đầu thai`, `Đánh quái`.

## 10. Asset extraction pipeline nên lưu lại nếu làm tiếp

```text
Input bundle
 -> check plain UnityFS/UnityRaw/UnityWeb
 -> if not plain: FG_Decrypt-compatible transform
 -> validate header/version/block table
 -> decompress UnityFS blocks
 -> parse serialized files/CAB
 -> export TextAsset/MonoBehaviour/prefab/config
 -> index names/IDs into database/
```

Khi có extractor ổn định, không nên chỉ lưu tool; cần commit **kết quả semantic** vào knowledge base để AI sau không cần decrypt lại.

## 11. Các file config text đã đọc trực tiếp

### `app.info`

- company: `FGStudio`
- product: `Thần Long  Mobile`

### `boot.config`

Có:

- graphics jobs enabled;
- threading mode 6;
- native debugger wait disabled;
- HDR disabled;
- GC max time slice 3;
- build GUID.

### `Version.xml`

Cho biết snapshot config có:

- application `VerCode=125`;
- CDN FGStudio;
- SDK endpoints cho server list/account operations;
- log service;
- voice blob service;
- `VoiceRealtime Enable=true Backend=livekit`.

### root `Manifest.xml`

Cho biết PC launcher manifest:

- `LauncherVersion=4`
- `GameVersion=126`
- `GameExeName="Thần Long  Mobile.exe"`
- Windows CDN path.

`VerCode=125` trong StreamingAssets và `GameVersion=126` ở root launcher manifest có thể phản ánh hai versioning layers khác nhau (app config vs PC package/launcher update), không nên ép thành cùng một số.

## 12. Ưu tiên nếu tiếp tục đào asset

1. Port/reuse exact `FG_Decrypt`.
2. Extract `Config.unity3d`.
3. Extract `Interface.unity3d` + shared UI bundles.
4. Build tables into `database/`.
5. Chỉ sau đó đào asset visual lớn nếu task cần.
