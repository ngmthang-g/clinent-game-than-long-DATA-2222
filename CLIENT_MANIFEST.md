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

Original bytes của archive nghiên cứu đã được đối chiếu với LFS object ID của `GameAssembly.dll`, `global-metadata.dat`, và `FGClientTool_Windows.dll`; cả ba đều exact-match. Deep-analysis docs hiện tại thuộc đúng snapshot này.

## Audit bổ sung 2026-08-26

Multipart archive do chủ sở hữu cung cấp đã được reconstruct và CRC-test toàn bộ:

- 77 ZIP entries;
- 64 regular files;
- 13 directories;
- 223,017,995 uncompressed file bytes;
- không có CRC-bad entry;
- SHA-256 manifest cho toàn bộ 64 file nằm ở `database/CLIENT_FILE_MANIFEST_SHA256.csv`.

Canonical audit:

- `analysis/36_ARCHIVE_BYTE_AUDIT_2026-08-26.md`

PC sync / hidden UI input evidence mới từ original `global-metadata.dat`:

- `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`

Audit phân biệt rõ hai trường hợp:

1. **path có trong repo nhưng GitHub API chỉ hiện LFS pointer** — không gọi là missing file;
2. **path thật sự không tồn tại trong repo** — archive audit hiện chỉ xác định 11 screenshot mới từ 2026-08-17 đến 2026-08-24 so với `Game/Screenshots` tại thời điểm audit. Đây là visual evidence, không phải thiếu core gameplay/runtime binary.

Expected primary snapshot hashes:

```text
GameAssembly.dll
4c98c9934bc4260efa64f5492c58e0c5104c89359f0126e7cd402feb381fe3c7

global-metadata.dat
d199498dad7d3139e4c09f6742f4645bfc2a33c465e3d259196931199f6ee6a8

FGClientTool_Windows.dll
cab5148fa70ae231e7245d62d8448b7881c16ed64bd8c84558f68e21d6ecd9a0
```

Nếu các primary hashes này khớp, đừng mặc định một lỗi resolver/runtime là do client khác version. Ưu tiên kiểm tra semantic resolver, init timing, PID/session, window/Screen/UI state và stale pointers trước.

## Không cần làm lại

Không yêu cầu user:

- hash lại client;
- upload client mới;
- xác định version lại;
- phân tích tổng quát lại GameAssembly.

Chỉ re-open original binary khi một task cụ thể cần exact disassembly/field/signature chưa có trong knowledge base.

## Entry point

Đọc `AI_INDEX.md` rồi `analysis/00_MASTER_RESEARCH_MAP.md`.
