# 36 — Byte-level audit of `ThanLongMobile_PC` multipart archive

Audit date: **2026-08-26**

Scope: the user-supplied multipart archive consisting of `ThanLongMobile_PC.z01`, `ThanLongMobile_PC.z02`, and the final `.zip` segment. This document records byte-level identity, archive integrity, repo delta, runtime/config fingerprints, and evidence boundaries. It does **not** replace the deeper semantic research already stored in this repository.

---

## 1. Bottom line

The supplied multipart archive is valid after proper split-ZIP reconstruction.

- ZIP central directory entries: **77**
- regular files: **64**
- directories: **13**
- total uncompressed file bytes: **223,017,995**
- total compressed payload bytes: **123,323,823**
- compressed/uncompressed ratio: **55.30%**
- every regular file uses Deflate
- Python `ZipFile.testzip()` result: **no CRC failure**
- earliest ZIP timestamp: **2026-03-01 09:38:48**
- latest ZIP timestamp: **2026-08-24 23:35:50**

The first important correction is terminology: the repository is **not missing the core gameplay files**. Many large `.dll`, `.exe`, and `.dat` paths are Git LFS objects, so GitHub's normal Contents API exposes a ~130-byte LFS pointer instead of the original binary. That is different from a path actually being absent.

The literal path delta found in this archive is currently **11 later screenshots**. Core gameplay/runtime/config sources are present in the repository.

Machine-readable per-file SHA-256/CRC/size data is stored in:

- `database/CLIENT_FILE_MANIFEST_SHA256.csv`

---

## 2. Multipart container identity

Original uploaded pieces:

| Part | Size | SHA-256 |
|---|---:|---|
| `ThanLongMobile_PC.z01` | 52,428,800 | `e8d90bff7d8a95870bb7e0950edeca8715ecba027f63bd28db454d23b5655772` |
| `ThanLongMobile_PC.z02` | 52,428,800 | `da8ac705f45b7c1f733609fbd2204d63b51e1fa2447fbb7c33142fc54c0e2c00` |
| final ZIP segment | 18,484,775 | `fd9fda93fd48f68fa23bf1df99f73b0cb2c4de34c6de02ff4da8fcf840e1ae71` |

Reconstructed single-volume ZIP:

- size: **123,342,371 bytes**
- SHA-256: `c487bb5c25b6de4ca672f177ff5447f65d6e715ba815853f980c640fa7b3c821`

The `.z01` begins with the split-archive marker and ZIP local-file signature. Concatenating split pieces as arbitrary bytes is not the preferred validation path; the archive was reconstructed as a split ZIP and then CRC-tested entry by entry.

---

## 3. Frozen snapshot identity vs Git LFS

Three primary binaries were independently hashed from the supplied original bytes and compared with the LFS OIDs already committed in this repository.

| Source | Original size | SHA-256 from archive | Result vs repo LFS OID |
|---|---:|---|---|
| `Game/GameAssembly.dll` | 61,923,328 | `4c98c9934bc4260efa64f5492c58e0c5104c89359f0126e7cd402feb381fe3c7` | **exact match** |
| `Game/Thần Long  Mobile_Data/il2cpp_data/Metadata/global-metadata.dat` | 14,747,552 | `d199498dad7d3139e4c09f6742f4645bfc2a33c465e3d259196931199f6ee6a8` | **exact match** |
| `Game/Thần Long  Mobile_Data/Plugins/x86_64/FGClientTool_Windows.dll` | 107,520 | `cab5148fa70ae231e7245d62d8448b7881c16ed64bd8c84558f68e21d6ecd9a0` | **exact match** |

Therefore this archive belongs to the same frozen research snapshot already used by the semantic knowledge base. It is not a second client version that should fork the research conclusions.

Other useful fingerprints:

| File | Size | SHA-256 |
|---|---:|---|
| `Game/UnityPlayer.dll` | 35,718,568 | `9feedb4527a30fae4762bff45d204f8e85b90851b2c8ae8d24f436f7d474667b` |
| `Game/Thần Long  Mobile.exe` | 667,648 | `53dbfb39b0e153966ef0dce20fa1d27423e481770a3575ff0934237c2b61f5c9` |
| `Launcher.exe` | 2,213,888 | `c4c1c49198799f2a6d1a1de93f40a48b6c382d901cc1bb09c42e2bb8ce4fe5f7` |
| `Host.exe` | 209,920 | `1d2db2590f48535d74b94343b380774fecdc72732934b30911748e16624c8698` |

Use these hashes before blaming CPU/Windows differences on a different client build. Same key hashes strongly narrow a failure toward runtime resolution, initialization, window/render/input state, configuration, or machine environment rather than missing methods caused by a different binary.

---

## 4. Literal archive-to-repository path delta

Directory-by-directory comparison found the gameplay/runtime/config paths represented in the archive already represented in `main`.

The archive contains **26 screenshots**. The checked repository screenshot directory currently contains entries through:

`TLM_20260814_134426_8204684.jpg`

The following **11 archive screenshots are not present as repository paths** at audit time:

| Screenshot | Size | SHA-256 |
|---|---:|---|
| `TLM_20260817_082632_4133710.jpg` | 300,779 | `14c2849a060bde535d72dedff19e4c07bca8e4955fc0c3d052663118119ec433` |
| `TLM_20260817_082635_0686503.jpg` | 300,379 | `d8daa058ce0b5771758baba16d6c9c5d1cc7f7811f98bb7a847e01704d623f6a` |
| `TLM_20260818_084926_4563233.jpg` | 198,482 | `925cdaab5ca3f1e35d82e83280bdedb9fb9ee8d0d82808467d750c74227ed090` |
| `TLM_20260818_115437_7015335.jpg` | 206,759 | `d9e437b7c27495665c4662a789ace1a5dd9178d7612f0863755a1908c37b5150` |
| `TLM_20260819_003940_8957376.jpg` | 184,778 | `36d8d76eb644556cf1da30b6440da3d3cb191fc229237de5d44e15f8b4c7b69c` |
| `TLM_20260820_053255_4558283.jpg` | 154,412 | `00da33aeff3e4e79c1df3e9f8f118e9054bfa764be0547b36e868ea706fda737` |
| `TLM_20260820_091153_0460283.jpg` | 211,911 | `f5c17da81bf5e6b8cfc7f5c279181c32f6e8a52e44dc3efc9e2bc7c705463ef3` |
| `TLM_20260820_091153_7773083.jpg` | 185,616 | `1bfd15759171d080530bfd9bb6ebb6acc12f61193b54334fbf9083cf317f54c6` |
| `TLM_20260820_092117_2748073.jpg` | 187,577 | `29c33aca2839c5a8dd5c9701d9278953b4e339108886933f5f374f95997103e4` |
| `TLM_20260821_010601_1398453.jpg` | 201,402 | `2b23f3ed2755cbd47f0d3ab833ffe5cbc343bb0bbdcdef1770f580b5771d6d4e` |
| `TLM_20260824_233550_5108794.jpg` | 145,352 | `7fc243f367de3887d6be0bb9088b897006db5fe99f30675feb878dc795cc3ac2` |

These are evidence/visual-regression files, not missing gameplay logic. Do not infer a missing runtime API from their absence.

---

## 5. Launcher/update identity

Root `Manifest.xml` records:

```text
CdnUrl=https://cdn.fgstudio.vn/windows
LauncherVersion=4
GameVersion=126
GameExeName=Thần Long  Mobile.exe
```

Both launcher config files target **.NET Framework 4.7.2**.

`Host.exe` and `Launcher.exe` are PE32 x86 managed/.NET binaries; the Unity game/native runtime is PE32+ x64. This confirms two separate execution layers:

```text
32-bit .NET launcher / updater / session control
              |
              v
64-bit Unity + IL2CPP game process
```

Do not mix launcher process-control APIs with per-game-process semantic gameplay actions.

---

## 6. Unity/runtime identity

`app.info`:

```text
FGStudio
Thần Long  Mobile
```

`boot.config` includes:

```text
gfx-enable-gfx-jobs=1
gfx-threading-mode=6
wait-for-native-debugger=0
hdr-display-enabled=0
gc-max-time-slice=3
build-guid=2de30840fb514ea7b116e23bd3a824a2
```

`global-metadata.dat`:

- size: **14,747,552 bytes**
- IL2CPP metadata magic: `0xFAB11BAF`
- metadata version: **39**

`ScriptingAssemblies.json` contains **132 assembly entries**. Relevant dependency families include:

- `Assembly-CSharp` / `Assembly-CSharp-firstpass`
- LiveKit
- Unity Burst / Collections
- Unity Purchasing / Services
- Google.Protobuf / protobuf-net
- Newtonsoft.Json
- Unity input/UI modules
- URP / Rendering

`RuntimeInitializeOnLoads.json` contains **25 initialization records**. A particularly important Assembly-CSharp startup record is:

```text
className = SyncBootstrap
methodName = AutoInit
loadTypes = 0
```

The record proves automatic startup registration for `SyncBootstrap`. Do not infer the exact implementation contract from the initializer alone; targeted evidence is documented separately in `analysis/37_INPUT_SYNC_STATIC_EVIDENCE.md`.

---

## 7. Network/service configuration visible in the shipped snapshot

`StreamingAssets/Version.xml` identifies separate service roles rather than one monolithic server path.

High-level endpoint families visible in the client include:

- content/update CDN: `cdn.fgstudio.vn`
- account/server SDK: `sdk.fgstudio.vn`
- client logs: `logs.fgstudio.vn`
- voice blob service: `voicesdk.fgstudio.vn`
- realtime voice backend: **LiveKit**

The client records:

- Application `VerCode=125`
- Android package `com.fgstudio.thanlongmobile`
- iOS App ID `6470350824`
- voice message support enabled
- realtime voice enabled
- realtime backend `livekit`

`GameVersion=126` in the launcher manifest and `VerCode=125` in `Version.xml` are distinct versioning layers. Their different values are not evidence of a corrupt or mixed archive by themselves.

---

## 8. Native module fingerprints

Static PE inspection confirms:

### `GameAssembly.dll`

- PE32+ x64 native
- sections include `.text`, `il2cpp`, `.rdata`, `.data`, `.pdata`, `.fptable`, `.reloc`
- **371 named exports** observed
- **241** named `il2cpp_*` exports
- **117** named `mono_*` compatibility exports

This is strong architecture evidence that reflection/class/method/field/runtime-invoke style IL2CPP APIs are exported. It does **not** mean every high-level game method is directly exported by name.

### `FGClientTool_Windows.dll`

Exactly three named exports were observed:

```text
FG_Decrypt
FG_Encrypt
HelloWorld
```

This keeps the custom asset-transform subsystem conceptually separate from IL2CPP gameplay reflection/runtime semantics.

### Other support modules

- `lib_burst_generated.dll`: **441** named exports observed; mostly generated/opaque Burst symbols
- `livekit_ffi.dll`: **383** named exports observed, including LiveKit FFI initialization/request/dispose functions

These modules should not be broad-reversed for normal NPC/item/train/buff logic unless a call path proves relevance.

### PE timestamp warning

Raw PE header timestamps were inspected, but managed launcher timestamps are implausible/future-dated. Treat PE timestamps as weak metadata and **not authoritative build dates**. File hashes and manifest/config identity are stronger evidence.

---

## 9. Bundle-level evidence

Important shipped asset states:

- `data.unity3d`: **47,627,199 bytes**, plaintext `UnityFS` header, version text `6000.3.6f1`
- `Config.unity3d`: **1,361,714 bytes**, custom-transformed/non-plain header
- `Interface.unity3d`: **578,379 bytes**, custom-transformed/non-plain header; contains Unity version/CAB evidence
- `Translations.unity3d`: **1,827,488 bytes**, transformed wrapper
- Interface shared bundles (`LoadingResources`, `Logo`, `Shared`, `Shared_2`) similarly require the known custom-transform handling

This audit does not redo bundle extraction because canonical research already proves successful Config/Interface extraction. Refer to `analysis/06_ASSETS_ENCRYPTION_BUNDLES.md` and the database catalogs instead of treating transformed first bytes as corruption.

---

## 10. PDB/source-layout evidence

Launcher PDB strings expose a concrete project layout such as:

```text
PCLauncher/Launcher/Launcher/MainWindow.xaml.cs
PCLauncher/Launcher/Launcher/Manager/GameInstanceSession.cs
PCLauncher/Launcher/Launcher/Manager/LauncherControlService.cs
PCLauncher/Launcher/Launcher/Manager/WindowArranger.cs
PCLauncher/Launcher/Launcher/Network/Downloader.cs
```

The PDB also exposes manager/models related to accounts, roles, scripts, groups, server selection, local secret protection, process helpers, and ZIP extraction.

This supports the existing conclusion that the official launcher has a substantial multi-instance/session/sync/record-playback layer. It still does not make launcher state interchangeable with live Unity object pointers inside any game PID.

---

## 11. What this archive does and does not add to the knowledge base

### Newly useful from this audit

1. reproducible whole-archive byte identity;
2. SHA-256/CRC/size manifest for all 64 files;
3. proof that primary LFS OIDs match the user-supplied original bytes;
4. precise distinction between Git LFS pointers and truly absent paths;
5. exact 11-screenshot path delta;
6. stronger launcher/update/runtime/dependency fingerprints;
7. targeted PC sync/input source-path evidence, documented separately.

### Already solved elsewhere; do not duplicate

- Config XML semantic extraction;
- Interface Lua/layout extraction;
- packet IDs and semantic actions;
- MainThread dispatcher architecture;
- NPC/map/path/item/skill/buff/team runtime schemas;
- broad GameAssembly architecture.

### Still not proven by this audit

- exact ABI/signature/parameter order of newly surfaced input-sync methods;
- exact UDP sync message wire format;
- exact screen/coordinate conversion chain used by `TryClickUI`;
- live behavior on a particular PC/GPU/CPU/window configuration;
- server acceptance semantics that require runtime tests.

Do not convert string existence into a made-up call contract.

---

## 12. Practical verification rule for future work

Before diagnosing a machine-specific resolver problem, compare at minimum:

```text
GameAssembly.dll SHA-256
+ global-metadata.dat SHA-256
+ FGClientTool_Windows.dll SHA-256 when bundle logic matters
```

For this frozen snapshot the expected first two are:

```text
GameAssembly.dll
4c98c9934bc4260efa64f5492c58e0c5104c89359f0126e7cd402feb381fe3c7

global-metadata.dat
d199498dad7d3139e4c09f6742f4645bfc2a33c465e3d259196931199f6ee6a8
```

If those match, a missing semantic symbol should not immediately be blamed on “different client files”. Investigate resolver assumptions and runtime state first.
