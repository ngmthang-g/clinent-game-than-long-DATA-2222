# File-by-file catalog — client snapshot

> Mục tiêu: future AI nhìn tên file là biết **file này là gì, có thể chứa gì, có đáng phân tích không và nên dùng khi nào**. Các bundle có nội dung dự đoán được gắn `PROBABLE` thay vì nói chắc.

## Root repository

### `.gitattributes`

**Role:** Git configuration, không phải client logic.

- cấu hình Git LFS cho `.dll`, `.dat`, `.exe`, `.bin`, `.bundle`;
- không phân tích để tìm game logic.

### `README.md`

**Role:** entry point của knowledge base.

### `AI_INDEX.md`

**Role:** AI routing/index. Phải đọc đầu tiên.

### `CLIENT_MANIFEST.md`

**Role:** định danh snapshot + nguồn binary chính.

### `Manifest.xml`

**Priority:** 2/5

Đã đọc trực tiếp:

- CDN Windows: `https://cdn.fgstudio.vn/windows`
- `LauncherVersion=4`
- `GameVersion=126`
- executable: `Thần Long  Mobile.exe`

**Use:** launcher/package versioning, update flow. Không chứa gameplay.

### `Host.exe`

**Priority:** 2.5/5

**Type:** .NET Framework 4.7.2 PE32 console/helper.

Đã thấy logic/string cho:

- manifest download;
- file download;
- CDN URL;
- game/launcher version;
- zip extraction;
- process kill/check;
- HTTP client.

**Use:** nghiên cứu updater/host orchestration, không phải gameplay.

### `Host.exe.config`

**Priority:** 1/5

Chỉ xác nhận .NET Framework 4.7.2 runtime.

### `Host.pdb`

**Priority:** 2/5 launcher, 0.5/5 gameplay

Debug symbols/PDB cho Host; hữu ích nếu decompile/reconstruct launcher host.

### `Launcher.exe`

**Priority:** 2.5–3/5 cho multi-client, 1/5 gameplay

**Type:** .NET Framework 4.7.2 WPF.

Đã thấy:

- account/session/process management;
- server selection;
- direct game launch;
- sync enable/master/group;
- recording/playback theo process/group;
- LauncherControlService;
- script list/manager-related strings.

**Use:** multi-account/process orchestration. Không thay thế per-process game runtime bridge.

### `Launcher.exe.config`

**Priority:** 1/5

.NET Framework 4.7.2 config.

### `Launcher.pdb`

**Priority:** 2.5/5 nếu reverse launcher

Có thể lộ source symbols/paths. Không ưu tiên cho gameplay IL2CPP.

---

# `Game/`

## `Game/GameAssembly.dll`

**Priority:** 5/5 — nguồn số 1 cho logic game.

**Type:** PE32+ x64 IL2CPP native.

**Contains / evidence:**

- Assembly-CSharp native gameplay;
- Lua bridge;
- Game/GUI/Network APIs;
- world/scene/path symbols;
- inventory/item APIs;
- skill/buff APIs;
- network processors/command names;
- extensive `il2cpp_*` exports.

**Use:** semantic resolver, class/method mapping, targeted disassembly.

**Do not:** re-scan toàn file cho mọi task; dùng docs/API quick reference trước.

## `Game/Thần Long  Mobile.exe`

**Priority:** 2/5

Unity Windows executable/bootstrap.

**Potential content:** process startup, module load, command line, Unity entry plumbing.

**Not primary:** gameplay logic đã nằm chủ yếu ở GameAssembly.

## `Game/UnityPlayer.dll`

**Priority:** 3/5

Unity native engine runtime.

**Contains:** GameObject/Component/Transform, PlayerLoop, AssetBundle, Input, rendering/engine internals.

**Use:** main-thread/Unity object/engine bridge questions.

## `Game/baselib.dll`

**Priority:** 1/5 gameplay

Unity low-level platform layer: memory/thread/socket/filesystem primitives.

## `Game/UnityCrashHandler64.exe`

**Priority:** 0.5/5 gameplay

Crash handling. Chỉ hữu ích khi debug crash reports/dumps.

## `Game/D3D12/D3D12Core.dll`

**Priority:** 0.5/5 gameplay

Graphics/Direct3D runtime. Không liên quan NPC/item/combat logic.

## `Game/Screenshots/*.jpg`

**Priority:** 1/5 logic; 2/5 UI context

Ảnh chụp trong game. Dùng để:

- đối chiếu visual UI;
- tên NPC/map/labels;
- regression screenshots.

Không dùng làm source-of-truth cho data khi API semantic tồn tại.

---

# `Game/Thần Long  Mobile_Data/`

## `app.info`

**Priority:** 1/5

Đã đọc:

```text
FGStudio
Thần Long  Mobile
```

Xác nhận company/product identity.

## `boot.config`

**Priority:** 2/5 architecture/debug

Đã đọc:

- `gfx-enable-gfx-jobs=1`
- `gfx-threading-mode=6`
- `wait-for-native-debugger=0`
- `hdr-display-enabled=0`
- `gc-max-time-slice=3`
- build GUID present.

**Use:** engine startup/performance/debug context.

## `ScriptingAssemblies.json`

**Priority:** 4/5 architecture inventory

Xác nhận managed assembly landscape trước IL2CPP:

- Assembly-CSharp / firstpass;
- UnityEngine modules;
- LiveKit;
- Burst/Collections/Mathematics;
- URP/render pipeline;
- Google.Protobuf + protobuf-net;
- Newtonsoft.Json;
- Unity Purchasing/Services;
- zlib.net, System.IO.Hashing, Unsafe, etc.

**Use:** biết dependency/subsystem nào tồn tại mà không scan binary lại.

## `RuntimeInitializeOnLoads.json`

**Priority:** 3.5/5

Đã thấy startup entries:

- `Assembly-CSharp.SyncBootstrap.AutoInit`;
- LiveKit `MonoBehaviourContext.Init`;
- `FfiClient.Init/GetMainContext`;
- Burst initializers;
- Unity Services/Purchasing registration;
- Unity thread info capture.

**Use:** bootstrap/main-thread/service initialization research.

## `data.unity3d`

**Priority:** 4/5

**Type:** plain `UnityFS` bundle ~47.6 MB.

**Version text:** `6000.3.6f1`.

**Potential:** serialized game/resource data. Có thể extract bằng standard Unity bundle tooling trước khi cần FG decrypt.

---

# `Plugins/x86_64/`

## `FGClientTool_Windows.dll`

**Priority:** 5/5 cho asset branch

**Type:** native x64 DLL riêng FGStudio.

**Exports verified:**

- `FG_Encrypt`
- `FG_Decrypt`
- `HelloWorld`

**Contains:** custom bundle transform/obfuscation logic; detect `UnityFS`, `UnityRaw`, `UnityWeb`; byte pair transforms; branch dùng `0x9E3779B9` + xorshift.

**Use:** phục hồi Config/Interface/custom bundles.

## `lib_burst_generated.dll`

**Priority:** 2/5

Unity Burst generated native jobs; nhiều hashed exports. Chỉ reverse targeted khi call graph chỉ vào đây.

## `livekit_ffi.dll`

**Priority:** 1/5 gameplay, 4/5 voice/media

LiveKit/WebRTC native stack: audio/video/PeerConnection/ICE/RTP/DataChannel/FFI.

`Version.xml` xác nhận voice realtime backend LiveKit.

---

# `Resources/`

## `unity default resources`

**Priority:** 1.5/5 gameplay

Unity built-in/default resources. Có version text riêng; không dùng để kết luận core client version.

---

# `il2cpp_data/Metadata/`

## `global-metadata.dat`

**Priority:** 5/5 — nguồn số 1 cùng GameAssembly.

**Verified:**

- IL2CPP metadata magic;
- version 39;
- ~16,080 type definitions;
- 96 images/assemblies;
- large method/field/parameter tables;
- string heap chứa class/method/enum/command names.

**Use:** map semantic namespace/class/method/field; tránh blind RVA-only reverse.

---

# `il2cpp_data/Resources/`

Các file resource hiện quan sát:

### `Newtonsoft.Json.dll-resources.dat`

**Priority:** 0.5/5 gameplay

Managed resource satellite/data cho Newtonsoft.Json. Gần như không có game logic.

### `System.Data.dll-resources.dat`

**Priority:** 0.5/5

Framework resource data.

### `System.Drawing.dll-resources.dat`

**Priority:** 0.5/5

Framework resource data.

### `System.ServiceModel.dll-resources.dat`

**Priority:** 0.5/5

Framework resource data.

### `mscorlib.dll-resources.dat`

**Priority:** 0.5/5

Core library resources. Không reverse trước gameplay.

---

# `StreamingAssets/`

## `Config.unity3d`

**Priority:** 5/5 predicted static-data value

Header custom/obfuscated.

**PROBABLE contents:** item/NPC/map/monster/skill/buff/magic/quest/portal config tables.

**Next action when needed:** run FG_Decrypt-compatible extraction, index TextAsset/MonoBehaviour/config outputs.

## `Interface.unity3d`

**Priority:** 4.5/5

Custom/obfuscated Unity bundle; binary still shows Unity/CAB/version traces.

**PROBABLE contents:** Lua/UI script definitions, prefab/resource names, callbacks for NPC/shop/revive/auto.

## `Translations.unity3d`

**Priority:** 3.5/5

Localization/text bundle candidate. Useful to map IDs/keys -> display names after extract.

## `UnityServicesProjectConfiguration.json`

**Priority:** 1.5/5 gameplay

Đã đọc:

- environment `production`;
- Unity Services Core version `1.16.0`;
- Unity Purchasing version `5.1.2`;
- initializer assembly names.

Useful for dependency inventory, not game mechanics.

## `UpdateList.xml`

**Priority:** 1/5

Snapshot hiện tại chứa empty `<UpdateList>`.

## `Version.xml`

**Priority:** 2.5/5 environment/network services

Đã đọc:

- CDN base;
- application VerCode 125;
- FGStudio account/server endpoints;
- log endpoint;
- voice blob service;
- voice realtime LiveKit enabled.

**Use:** service landscape, not internal combat/item logic.

---

# `StreamingAssets/Interface/`

## `LoadingResources.unity3d`

**Priority:** 2.5/5 UI

Likely loading-screen/shared UI resources. Header custom.

## `Logo.unity3d`

**Priority:** 1/5 logic

Likely logo/branding resources. Low gameplay value.

## `Shared.unity3d`

**Priority:** 3/5 UI/resource

Shared interface bundle; may hold prefabs/materials/scripts/resources reused by multiple UIs.

## `Shared_2.unity3d`

**Priority:** 3/5 UI/resource

Second shared interface bundle; same reasoning as Shared.

---

# Giá trị reverse tổng hợp

## Tier S — phân tích trước

1. `GameAssembly.dll`
2. `global-metadata.dat`
3. `FGClientTool_Windows.dll`
4. `Config.unity3d`
5. `Interface.unity3d`

## Tier A

6. `data.unity3d`
7. Interface shared bundles
8. `Translations.unity3d`
9. `ScriptingAssemblies.json`
10. `RuntimeInitializeOnLoads.json`

## Tier B

11. `UnityPlayer.dll`
12. Launcher/Host nếu task liên quan multi-client/update/session
13. `lib_burst_generated.dll` targeted only

## Tier C

- LiveKit cho gameplay tasks
- baselib
- D3D12
- crash handler
- framework resource `.dat`
- logos/screenshots (trừ UI context)

# Critical interpretation rule

Tên file/bundle chỉ cung cấp context. Những câu như “Config chắc chắn chứa NPC table X” phải giữ `PROBABLE` cho tới khi extract thấy table cụ thể. Ngược lại, structural facts như IL2CPP metadata, exports, method names, bundle header, launcher CLR type là VERIFIED.
