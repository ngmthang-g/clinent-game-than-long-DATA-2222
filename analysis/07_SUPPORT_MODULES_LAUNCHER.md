# Support modules / Launcher / Host / file priority

## 1. UnityPlayer.dll

Role: Unity native engine runtime.

Giá trị reverse: **trung bình**.

Có engine functionality liên quan:

- GameObject / Component / Transform;
- PlayerLoop;
- AssetBundle;
- Input;
- rendering/graphics;
- engine object lifecycle.

Nó hữu ích khi cần bridge Unity internals hoặc hiểu main-thread/engine object behavior. Nhưng gameplay Thần Long chủ yếu nằm trong `GameAssembly.dll`, nên không reverse UnityPlayer trước nếu task là NPC/item/combat/UI logic.

## 2. lib_burst_generated.dll

Role: native code do Unity Burst sinh.

Giá trị reverse hiện tại: **thấp-trung bình**.

Đã thấy nhiều export (~441 trong lần inspection trước), phần lớn tên hash/opaque, cùng các initializer kiểu:

- `burst.initialize.statics...`
- `burst.initialize.externals...`

Có thể chứa job cho transform/rendering/data processing. Chỉ quay lại đây khi metadata/call graph chứng minh subsystem cần nghiên cứu được Burst compile.

## 3. livekit_ffi.dll

Role: LiveKit/WebRTC native FFI.

Giá trị gameplay: **thấp**.

Export/string evidence liên quan:

- AudioTrack / VideoTrack;
- PeerConnection;
- ICE / RTP;
- DataChannel;
- DesktopCapturer;
- `livekit_ffi_request`.

`Version.xml` xác nhận voice realtime bật và backend `livekit`, nên đây gần như chắc chắn là stack voice realtime/media, không phải entity/HP/inventory.

Không nên mất thời gian reverse file 24 MB này cho auto train/buff/sell.

## 4. baselib.dll

Role: Unity low-level platform abstraction.

Giá trị gameplay: **thấp**.

Chủ yếu cung cấp primitive như:

- socket/network low-level;
- thread/semaphore;
- memory;
- filesystem;
- platform/runtime plumbing.

Chỉ cần nếu debug lỗi engine/thread/socket ở mức rất thấp.

## 5. D3D12Core.dll

Role: Direct3D 12 runtime component.

Giá trị gameplay: **rất thấp**.

Không liên quan trực tiếp NPC/item/combat. Chỉ relevant khi xử lý rendering/graphics compatibility.

## 6. UnityCrashHandler64.exe

Role: Unity crash handler.

Giá trị reverse gameplay: **rất thấp**.

Có thể hữu ích gián tiếp khi phân tích crash dump/log, nhưng không phải nguồn game logic.

## 7. Thần Long Mobile.exe

Role: Unity player executable/bootstrap cho Windows client.

Giá trị reverse: **thấp-trung bình**.

Gameplay IL2CPP nằm ở GameAssembly. EXE quan trọng hơn cho:

- startup command line;
- module loading;
- process identity;
- bootstrap/runtime initialization.

Không ưu tiên để tìm player HP/item methods.

## 8. Host.exe

Inspection bản binary thực cho thấy:

- PE32 .NET/Mono/.NET assembly x86;
- target runtime .NET Framework 4.7.2 theo config;
- namespace/type strings thuộc `FGStudio.Launcher.Host`;
- chứa downloader/update logic.

Các string/type đáng chú ý:

- `LauncherManifestData`
- `Downloader`
- `DownloadManifestAsync`
- `DownloadFileAsync`
- `GameExeName`
- `CdnUrl`
- `GameVersion`
- `LauncherVersion`
- process helpers;
- zip extract logic;
- HTTP client.

### Diễn giải

Host là thành phần launcher/updater, không phải gameplay client. Có thể dùng để hiểu package update/download/extract.

## 9. Launcher.exe

Inspection binary thực:

- PE32 .NET WPF GUI;
- .NET Framework 4.7.2;
- chứa launcher UI, update logic và đáng chú ý là multi-instance/control/record-playback related functionality.

Strings/types đáng chú ý:

- `GameInstanceSession`
- `LauncherControlService`
- `GetSelectedClientProcessIds`
- `StartPlaybackForProcessAsync`
- `StopPlaybackForProcessAsync`
- group/process playback variants;
- `SendAutoLoginConfigAsync`
- `SetSyncEnabledAsync`
- `SetMasterAsync`
- `SetSyncGroupAsync`
- `RequestSyncStatesAsync`
- `RequestScriptListAsync`
- `StartRecordingAsync`
- `StopRecordingAsync`
- server selection;
- `BuildGameLaunchArguments`
- `LaunchGameDirect`
- account/session controls.

### Quan trọng

Launcher này có vẻ đã có một tầng multi-account/sync/record-playback riêng. Điều đó có thể hữu ích nếu cần hiểu cách official/client launcher quản lý nhiều process, nhưng **không được nhầm với gameplay internal action API**.

Nếu mục tiêu là auto nhiều client, có hai lớp độc lập:

```text
Launcher/session layer
 -> start/stop/select/sync multiple processes

Per-process game layer
 -> each client has its own runtime pointers/state/action queue
```

Không chia sẻ runtime object pointer giữa process.

## 10. PDB files

Repo có `Host.pdb` và `Launcher.pdb`.

Giá trị:

- có thể lộ source path/symbol/debug names;
- rất hữu ích để reverse .NET launcher nếu cần;
- không giúp đáng kể cho IL2CPP gameplay.

Launcher binary có source/debug path evidence kiểu PCLauncher project path, củng cố rằng đây là FGStudio launcher code.

## 11. ScriptingAssemblies.json

Giá trị: **cao cho architecture inventory**, dù file nhỏ.

Nó xác nhận stack:

- Unity 6 modules;
- Assembly-CSharp;
- LiveKit;
- Burst/Collections;
- URP;
- protobuf + protobuf-net;
- Newtonsoft.Json;
- Unity Purchasing/Services.

Đây là file AI nên đọc để biết dependency landscape mà không scan strings lại.

## 12. RuntimeInitializeOnLoads.json

Giá trị: **trung bình-cao** cho startup model.

Đáng chú ý:

- `Assembly-CSharp.SyncBootstrap.AutoInit`;
- LiveKit init;
- Burst direct call initializers;
- Unity Services/Purchasing init;
- Unity thread information capture.

Tên `SyncBootstrap.AutoInit` đáng lưu ý khi điều tra bootstrap/synchronization subsystem, nhưng chưa có đủ evidence để khẳng định chức năng cụ thể của `SyncBootstrap` ngoài việc nó auto-initialize.

## 13. Screenshots

Giá trị reverse logic: thấp.

Giá trị đối chiếu:

- UI labels/layout;
- visual state;
- map/NPC names;
- regression evidence.

Không nên dùng screenshot làm source-of-truth khi game data/API đã có semantic identifiers.

## 14. Tóm tắt ưu tiên file

| File/nhóm | Giá trị cho gameplay RE |
|---|---|
| GameAssembly.dll | 5/5 |
| global-metadata.dat | 5/5 |
| Config.unity3d | 5/5 dự đoán, cần extract |
| FGClientTool_Windows.dll | 5/5 cho asset decrypt |
| Interface bundles | 4.5/5 cho UI/Lua |
| data.unity3d | 4/5 |
| ScriptingAssemblies/RuntimeInitialize JSON | 3.5/5 |
| UnityPlayer.dll | 3/5 |
| Launcher/Host | 2.5/5, chủ yếu launcher/multi-instance |
| lib_burst_generated.dll | 2/5 |
| livekit_ffi.dll | 1/5 gameplay |
| baselib/D3D12/crash handler | 1/5 gameplay |
