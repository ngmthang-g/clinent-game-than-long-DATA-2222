# File-by-file catalog — frozen client snapshot

> Mục tiêu: future AI nhìn tên file là biết **file này là gì, chứa loại dữ liệu gì, giá trị reverse ở mức nào, và khi nào mới cần mở lại**.

Evidence rule:

- **VERIFIED** = đã đọc trực tiếp / metadata / disassembly / bundle extraction xác nhận.
- **PROBABLE** = dự đoán mạnh nhưng chưa có extraction/evidence đủ để coi là fact.
- Không được giữ một dự đoán cũ là `PROBABLE` nếu phase sau đã extract và chứng minh nó.

---

# Repository root

## `.gitattributes`

**Priority:** 0/5 gameplay

Git/LFS configuration only. Không có logic client.

## `README.md`, `AI_BOOTSTRAP.md`, `AI_ROUTER.md`, `AI_INDEX.md`

**Role:** knowledge-base navigation, không phải binary evidence.

AI build bình thường phải đi:

`AI_BOOTSTRAP -> AI_ROUTER -> one context pack -> required docs/database lookup`.

## `KB_METHOD.md`

Evidence/preservation policy. Dùng để phân biệt VERIFIED / PROBABLE / HYPOTHESIS và quy tắc lưu kiến thức.

## `CLIENT_MANIFEST.md`

Snapshot identity / source inventory. Repo này được owner giữ frozen; không cần broad version re-check mỗi session.

## `Manifest.xml`

**Priority:** 2/5

**VERIFIED:**

- CDN Windows: `https://cdn.fgstudio.vn/windows`
- `LauncherVersion=4`
- `GameVersion=126`
- executable: `Thần Long  Mobile.exe`.

Use: launcher/package/update context; không phải gameplay.

## `Host.exe`

**Priority:** 2.5/5 launcher; <1/5 gameplay

**VERIFIED type:** .NET Framework 4.7.2 PE32 helper/console.

Observed responsibilities include manifest/file download, CDN/version handling, zip extraction, process kill/check and HTTP client behavior.

Use only for update/host orchestration questions.

## `Host.exe.config`

**Priority:** 1/5

Runtime config; confirms .NET Framework target.

## `Host.pdb`

**Priority:** 2/5 launcher; ~0 gameplay

Debug symbols for Host. Useful only when reconstructing launcher/host internals.

## `Launcher.exe`

**Priority:** 2.5–3/5 multi-client/session; 1/5 gameplay

**VERIFIED type:** .NET Framework 4.7.2 WPF.

Observed areas:

- account/session/process management;
- server selection/direct launch;
- sync/master/group concepts;
- recording/playback process/group behavior;
- launcher control/service/script-manager strings.

This is not the canonical gameplay runtime source. Do not let launcher reverse distract Auto/skill/item/NPC tasks.

## `Launcher.exe.config`

**Priority:** 1/5

Framework config only.

## `Launcher.pdb`

**Priority:** 2.5/5 if launcher task exists

Potentially useful source symbols/paths; not a gameplay priority.

---

# `Game/`

## `Game/GameAssembly.dll`

**Priority:** 5/5 — Tier S

**VERIFIED type:** Windows x64 Unity IL2CPP native image.

Contains/recovered:

- Assembly-CSharp gameplay methods;
- Lua bridge and shared-data APIs;
- Game/GUI/Network API implementations;
- world/path/inventory/skill/buff symbols;
- packet processors and protocol vocabulary;
- `FGStudio.Engine.Utilities.MainThread` dispatcher;
- broad `il2cpp_*` runtime exports.

Use:

- semantic class/method resolution;
- exact missing native contract;
- targeted disassembly.

Do **not** start every feature by re-scanning this binary. Lua/Config/database often answer the question more cheaply.

## `Game/Thần Long  Mobile.exe`

**Priority:** 2/5

Unity Windows bootstrap executable. Useful for process/startup/module-load questions, not core gameplay logic.

## `Game/UnityPlayer.dll`

**Priority:** 3/5 engine; 1–2/5 normal gameplay feature

Unity native engine runtime: PlayerLoop, GameObject/Component/Transform, asset/render/input engine machinery.

Use only when the missing problem is genuinely engine-level. Main gameplay semantics are already better exposed through GameAssembly/Lua.

## `Game/baselib.dll`

**Priority:** 1/5 gameplay

Unity low-level platform primitives (memory/thread/socket/filesystem). Targeted debugging only.

## `Game/UnityCrashHandler64.exe`

**Priority:** 0.5/5 gameplay

Crash-report helper. Useful only for crash/debug investigations.

## `Game/D3D12/D3D12Core.dll`

**Priority:** 0.5/5 gameplay

Graphics runtime. Ignore for NPC/item/skill/auto research.

## `Game/Screenshots/`

**Priority:** 1/5 logic; 2/5 UI context

Visual evidence only. Useful for matching visible labels/layout; semantic API/config data wins whenever available.

---

# `Game/Thần Long  Mobile_Data/`

## `app.info`

**Priority:** 1/5

**VERIFIED:** company/product identity:

```text
FGStudio
Thần Long  Mobile
```

## `boot.config`

**Priority:** 2/5 architecture/debug

Observed values include graphics jobs/threading, debugger setting, HDR flag, GC time slice and build GUID.

Use for engine startup/performance context only.

## `ScriptingAssemblies.json`

**Priority:** 4/5 architecture inventory

**VERIFIED:** pre-IL2CPP managed assembly/dependency landscape includes Assembly-CSharp, UnityEngine modules, LiveKit, Burst/Collections/Mathematics, URP/render pipeline, protobuf libraries, Newtonsoft.Json, Unity Purchasing/Services and framework dependencies.

Very useful as a dependency map; no need to rediscover which managed subsystems exist.

## `RuntimeInitializeOnLoads.json`

**Priority:** 3.5/5 bootstrap

**VERIFIED observed startup entries include:**

- `Assembly-CSharp.SyncBootstrap.AutoInit`;
- LiveKit `MonoBehaviourContext.Init`;
- FFI client initialization/main-context acquisition;
- Burst initialization;
- Unity Services/Purchasing registration;
- Unity thread-info capture.

Use for bootstrap/main-thread/service initialization questions.

## `data.unity3d`

**Priority:** 4/5 asset/resource branch

**VERIFIED file:** plain large Unity bundle (~47.6 MB) with UnityFS/version evidence (`6000.3.6f1`).

Unlike Config/Interface, this file is not currently the primary semantic KB source. It may contain serialized/resource data valuable for model/prefab/resource questions.

Recommended rule:

- inspect it only when a task needs asset/resource content not already present in Config/Interface/Lua/metadata;
- do not parse 47 MB merely because it exists.

---

# `Plugins/x86_64/`

## `FGClientTool_Windows.dll`

**Priority:** 5/5 asset/decrypt branch — Tier S

**VERIFIED exports:**

- `FG_Encrypt`
- `FG_Decrypt`
- `HelloWorld`.

Reverse work recovered the custom bundle transform sufficiently to extract important shipped Config/Interface data. It recognizes Unity bundle signatures and contains custom transformation/xorshift-style logic.

Its major research job is already accomplished. Reopen only if another FG-obfuscated bundle cannot be decoded with the existing method.

## `lib_burst_generated.dll`

**Priority:** 2/5

Burst-generated native jobs with hashed/generated exports. Targeted only when a call graph proves an important algorithm lives there.

## `livekit_ffi.dll`

**Priority:** 1/5 gameplay; 4/5 voice/media

LiveKit/WebRTC native stack (audio/video/PeerConnection/ICE/RTP/DataChannel/FFI).

Use for realtime voice/media questions, not Train/Buff/Sell/NPC logic.

---

# `Resources/`

## `unity default resources`

**Priority:** 1.5/5 gameplay

Unity built-in resource data. Do not use its embedded version text as the canonical game/client version.

---

# `il2cpp_data/Metadata/`

## `global-metadata.dat`

**Priority:** 5/5 — Tier S, paired with GameAssembly

**VERIFIED:**

- IL2CPP metadata magic/version 39;
- ~16,080 type definitions;
- 96 images/assemblies;
- large method/field/parameter/string tables.

Use:

- semantic namespace/class/method/field/token lookup;
- method identity before native disassembly;
- enum/command/type discovery.

Do not rely on guessed RVA alone when metadata identity exists.

---

# `il2cpp_data/Resources/`

Observed framework resource files:

- `Newtonsoft.Json.dll-resources.dat`
- `System.Data.dll-resources.dat`
- `System.Drawing.dll-resources.dat`
- `System.ServiceModel.dll-resources.dat`
- `mscorlib.dll-resources.dat`.

**Priority:** ~0.5/5 gameplay

Managed/framework resources, not primary game logic.

---

# `StreamingAssets/`

## `Config.unity3d`

**Priority:** 5/5 — Tier S semantic data

**STATUS: VERIFIED EXTRACTED.**

This is no longer merely a “likely config bundle”. The custom bundle path was decoded and produced **75 Config XML TextAssets**.

High-value confirmed tables include:

- `NPCs` — 1,003
- `Maps` — 193
- `AutoPath` — 1,618 records
- `Items` — 5,238
- `Equips` — 22,763
- `Skills` — 2,091
- `SkillProperties` — 2,044
- `AutoSkills` — 300
- `MagicAtrributes` — 509
- `Monsters` — 17,121
- `Tasks` — 516
- `Pets` — 8,349
- `Spirits` — 1,889
- `Factions` — 17
- `FuBenScenarios` — 19
- plus dozens of equipment, guild, activity, cosmetic/model tables.

Canonical navigation:

- `database/CONFIG_TABLE_CATALOG.md`
- `analysis/32_CONFIG_DOMAIN_ATLAS.md`
- `analysis/33_UNDEREXPLORED_HIGH_VALUE_CONFIG.md`.

Future AI should query normalized/docs first instead of decrypting this bundle again.

## `Interface.unity3d`

**Priority:** 5/5 — Tier S UI/Lua semantic data

**STATUS: VERIFIED EXTRACTED.**

Recovered semantic content includes:

- **338 UI layout XML TextAssets**;
- **1,469 handler bindings**;
- **339 Lua script classes with colon-method definitions**;
- global infrastructure such as `Global`, `Global_Constants`, `Global_Functions`, `Loader`, `TCPCmdHandler`, `TCPCmdEventHandler`, `TCPPacketDefine`;
- readable scripts for AutoFight, AutoHp, Utilities, Revival, NPCShop, Bag, GameDialog, Task, Team, Pet and other systems.

This bundle is one of the most valuable discoveries in the repo because Lua often exposes exact action/payload/state logic in human-readable form.

Future order for a visible UI feature:

`layout binding -> same-name Lua -> runtime/API/packet -> native only if still missing`.

Canonical docs:

- `analysis/09_PHASE2_DECRYPTED_DATA_LUA.md`
- `database/LUA_SCRIPT_CATALOG.md`
- `database/UI_LAYOUT_CALLBACKS.md`.

## `Translations.unity3d`

**Priority:** 3.5/5 localization

**STATUS:** bundle exists (~1.83 MB). Full normalized localization database is not currently canonical in the KB.

**PROBABLE value:** display-string/localization key mapping, useful when semantic IDs exist but user-facing names/text are missing.

Target only when translation/display-text lookup becomes a blocker.

## `UnityServicesProjectConfiguration.json`

**Priority:** 1.5/5 gameplay

**VERIFIED:** production environment plus Unity Services/Purchasing package configuration.

Dependency context only.

## `UpdateList.xml`

**Priority:** 1/5

Snapshot contains empty `<UpdateList>`.

## `Version.xml`

**Priority:** 2.5/5 service/environment

**VERIFIED observed:** CDN/application code and FGStudio account/server/log/voice service endpoints; realtime voice uses LiveKit.

Useful for service landscape, not combat/item logic.

---

# `StreamingAssets/Interface/`

## `LoadingResources.unity3d`

**Priority:** 2.5/5 UI resources

Likely loading/shared resource bundle. Not a semantic gameplay priority unless a concrete UI asset is needed.

## `Logo.unity3d`

**Priority:** 1/5 logic

Branding resources.

## `Shared.unity3d`, `Shared_2.unity3d`

**Priority:** 3/5 UI/resource

Shared interface resources/prefabs/materials likely reused by multiple UIs. Target only for asset/prefab questions that Interface Lua/layout text cannot answer.

---

# Current reverse priority after completed phases

The original “Tier S files” are not all equally unfinished anymore.

## Solved/mostly harvested semantic sources

1. `Config.unity3d` — decrypted/extracted, 75 tables cataloged.
2. `Interface.unity3d` — decrypted/extracted, Lua/layout/handlers cataloged.
3. `GameAssembly.dll` + `global-metadata.dat` — broad semantic/native mapping done; only targeted missing contracts should be reversed.
4. `FGClientTool_Windows.dll` — decrypt branch sufficiently understood for the successful extraction work.

## Still worth targeted inspection when a concrete task demands it

1. `data.unity3d` — assets/serialized game resources.
2. `Translations.unity3d` — localization/text lookup.
3. shared Interface bundles — prefab/resource-specific questions.
4. UnityPlayer — engine-level/thread/object lifecycle issues only.
5. launcher/host — only multi-client/update/session tasks.
6. Burst — only when a proven call path enters generated job code.

## Normally ignore for gameplay knowledge

- LiveKit unless voice/media task;
- baselib;
- D3D12;
- crash handler;
- framework `.dat` resources;
- logos/screenshots except visual correlation.

---

# Critical future-AI rule

Do not repeat the old phase-1 assumption that Config/Interface contents are only predictions. Their major semantic contents have been extracted and documented.

At the same time, do not over-promote still-unread bundles such as Translations/shared resources into VERIFIED content claims. Preserve the distinction:

```text
extracted evidence = VERIFIED
filename/header expectation only = PROBABLE
```
