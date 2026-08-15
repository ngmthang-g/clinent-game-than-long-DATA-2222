# Client Snapshot Manifest

Repository: `ngmthang-g/clinent-game-than-long-DATA-2222`
Branch: `main`
Status: **FROZEN RESEARCH SNAPSHOT**

## Mục đích

Repo này không được dùng như nơi cập nhật client liên tục. Chủ sở hữu dự kiến giữ nguyên bộ client hiện tại để làm nguồn binary/data cố định cho knowledge base. Vì vậy future AI không cần yêu cầu hash lại mỗi lần làm việc.

## Identity đã ghi nhận

- Company/product từ `app.info`: `FGStudio` / `Thần Long  Mobile`
- Root PC manifest: `GameVersion=126`, `LauncherVersion=4`
- Streaming `Version.xml`: `Application VerCode=125`
- Game executable: `Thần Long  Mobile.exe`
- Architecture: Windows x64 game client
- Runtime architecture: Unity + IL2CPP
- IL2CPP metadata version: `39`
- Unity family: Unity 6 / `6000.3.x`
- `data.unity3d` version text: `6000.3.6f1`
- `Interface.unity3d` contains version text: `6000.3.7f1`

`GameVersion=126` và `VerCode=125` là hai versioning layers được đọc từ hai manifest/config khác nhau; không coi chúng là mâu thuẫn nếu chưa biết release/update semantics chính xác.

## Primary reverse-engineering sources

### Logic / schema

- `Game/GameAssembly.dll`
- `Game/Thần Long  Mobile_Data/il2cpp_data/Metadata/global-metadata.dat`

### Static data / assets

- `Game/Thần Long  Mobile_Data/data.unity3d`
- `Game/Thần Long  Mobile_Data/StreamingAssets/Config.unity3d`
- `Game/Thần Long  Mobile_Data/StreamingAssets/Interface.unity3d`
- `Game/Thần Long  Mobile_Data/StreamingAssets/Interface/*.unity3d`
- `Game/Thần Long  Mobile_Data/StreamingAssets/Translations.unity3d`

### Custom asset transform

- `Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll`

### Engine/support

- `Game/UnityPlayer.dll`
- `Game/Thần Long  Mobile_Data/Plugins/x86_64/lib_burst_generated.dll`
- `Game/Thần Long  Mobile_Data/Plugins/x86_64/livekit_ffi.dll`
- `Game/baselib.dll`

### Launcher/session layer

- `Host.exe`
- `Launcher.exe`
- their configs/PDBs

## LFS note

Các `.dll/.exe/.dat` lớn được Git LFS quản lý. GitHub Contents API có thể trả pointer text ~130 bytes thay vì original binary. Không phân tích LFS pointer như thể đó là DLL thật.

Original bytes của archive nghiên cứu đã được đối chiếu với LFS object ID của `GameAssembly.dll` và `global-metadata.dat`, nên deep-analysis docs hiện tại thuộc đúng snapshot này.

## Không cần làm lại

Không yêu cầu user:

- hash lại client;
- upload client mới;
- xác định version lại;
- phân tích tổng quát lại GameAssembly.

Chỉ re-open original binary khi một task cụ thể cần exact disassembly/field/signature chưa có trong knowledge base.

## Entry point

Đọc `AI_INDEX.md` rồi `analysis/00_MASTER_RESEARCH_MAP.md`.
