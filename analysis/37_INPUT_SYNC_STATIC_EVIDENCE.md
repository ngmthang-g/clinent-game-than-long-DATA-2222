# 37 — PC InputSync / hidden UI click static evidence

Source snapshot: the verified frozen client whose `GameAssembly.dll` and `global-metadata.dat` hashes match `CLIENT_MANIFEST.md` and `database/CLIENT_FILE_MANIFEST_SHA256.csv`.

Purpose: preserve exact static evidence relevant to PC multi-instance input synchronization, internal UI click/drag handling, and machine-specific resolver failures. This document intentionally separates **verified symbols** from **unproven ABI/runtime assumptions**.

---

## 1. Why this subsystem matters

The shipped client contains an explicit PC synchronization subsystem. It is not necessary to invent one from generic Windows input APIs.

Static metadata exposes a project folder literally named:

```text
Assets\Scripts\Game\Logic\PCSysnc\
```

The spelling `PCSysnc` is preserved exactly as found in metadata.

This subsystem sits conceptually between:

```text
launcher/session control
        |
        v
per-game PC sync bootstrap / registry
        |
        v
input capture / sync / injection
        |
        v
Unity UI pointer/drag state
```

That is separate from normal gameplay semantic APIs such as `Game.MoveTo`, `Game.UseSkill`, NPC/shop packets, etc.

---

## 2. Verified source-file paths from IL2CPP metadata

The following source paths are directly present as readable metadata evidence:

```text
Assets\Scripts\Game\Logic\PCSysnc\InputRecorder.cs
Assets\Scripts\Game\Logic\PCSysnc\InputSyncManager.cs
Assets\Scripts\Game\Logic\PCSysnc\InstanceRegistry.cs
Assets\Scripts\Game\Logic\PCSysnc\LauncherAutoLoginState.cs
Assets\Scripts\Game\Logic\PCSysnc\LauncherControlBridge.cs
Assets\Scripts\Game\Logic\PCSysnc\SyncBootstrap.cs
Assets\Scripts\Game\Logic\PCSysnc\SyncInput.cs
Assets\Scripts\Game\Logic\PCSysnc\SyncInputModule.cs
Assets\Scripts\Game\Logic\PCSysnc\SyncOverlayUI.cs
Assets\Scripts\Game\Logic\PCSysnc\UnityMainThreadDispatcher.cs
Assets\Scripts\Game\Logic\PCSysnc\WindowAspectLocker.cs
```

UI-side paths relevant to the same problem include:

```text
Assets\Scripts\LuaSystem\GUI\Button\UIButton.cs
Assets\Scripts\Engine\Utilities\Unity\UI\UIDragableObject.cs
```

These paths are stronger evidence than guessing from runtime logs because they identify the intended client source organization.

---

## 3. Verified type names

Readable metadata exposes at least these types/nested types:

```text
InputRecorder
InputRecorder|RecordedEvent
InputSyncManager
InputSyncManager|PendingMessage
InstanceRegistry
LauncherAutoLoginState
LauncherAutoLoginState|LoginConfig
LauncherControlBridge
LauncherControlBridge|LauncherControlMessageDto
LauncherControlBridge+LauncherControlMessageDto|LauncherRoleItemDto
SyncBootstrap
SyncBootstrapHelper
SyncInput
SyncInputModule
SyncOverlayUI
UnityMainThreadDispatcher
WindowAspectLocker
WindowAspectLocker|RECT
FGStudio.LuaSystem.GUI|UIButton
FGStudio.Engine.Utilities.Unity.UI|UIDragableObject
```

The exact nesting separator above follows the readable metadata/string representation. Treat it as type-identity evidence, not a C# declaration reconstruction.

---

## 4. Startup evidence

`RuntimeInitializeOnLoads.json` contains an Assembly-CSharp initializer:

```text
className  = SyncBootstrap
methodName = AutoInit
loadTypes  = 0
isUnityClass = false
```

Therefore the PC sync bootstrap is registered for automatic runtime initialization.

Important boundary:

- **verified:** `SyncBootstrap.AutoInit` is a runtime initializer;
- **not yet verified here:** exact initialization order relative to every Unity input/UI manager and exact conditions that can disable/fail it.

A resolver that scans too early can therefore fail even when the binary contains every expected symbol.

---

## 5. InputSyncManager semantic surface seen in metadata

The following names are directly present and are high-value anchors:

```text
InputSyncManager
SetSyncEnabled
SetSyncGroup
SetSyncState
get_SyncGroupId
GetSyncGroupId
SyncGroupId
syncGroupId
InjectSyncInput
FramePressState
TryClickUI
UpdateUIDrag
EndUIDrag
CancelUIDragState
ResetUIDragState
_uiDragging
_uiDragTarget
_uiDragData
GetLastPointerEventData
```

Do **not** assume this list is one class's complete public API. Static string/name presence does not by itself recover declaring type, access modifier, overload, parameter order, native address, or calling convention for every symbol.

Still, the combination gives a very strong semantic model:

```text
capture/sync input state
 -> inject input
 -> maintain per-frame press state
 -> attempt direct UI hit/click
 -> maintain UI drag state
 -> finish/cancel/reset drag
```

This is much more specific than a generic `SendInput`-style model.

---

## 6. UIButton and Unity UI evidence

The shipped metadata contains:

```text
FGStudio.LuaSystem.GUI|UIButton
HandleClickEvent
```

It also contains Unity/UI pointer and draggable-object evidence, including:

```text
UIDragableObject
GetLastPointerEventData
_uiDragging
_uiDragTarget
_uiDragData
UpdateUIDrag
EndUIDrag
CancelUIDragState
ResetUIDragState
```

Practical interpretation:

1. There is a game-owned `UIButton` abstraction with a semantic click handler.
2. There is a separate pointer/drag-state layer.
3. A robust hidden-click implementation must not treat “press” alone as necessarily equivalent to a complete click.
4. Failing to resolve or clean up drag/pointer state can plausibly explain a click path that works on one machine but fails or gets stuck on another.

What is **not** proven from names alone is the exact order required by `TryClickUI`, whether it directly invokes `UIButton.HandleClickEvent`, and which screen-space conversion helper it requires.

---

## 7. Runtime log strings — verified behavior clues

Readable client strings include these templates:

```text
[InputSyncManager] Fixed Master = Instance #{0}
[InputSyncManager] Fixed Master = {0}
[InputSyncManager] Fixed Master OFF ... focus-based
[InputSyncManager] Sync {0} | Instance #{1}
[InputSyncManager] SyncGroup = {0} | Instance #{1}
[InputSyncManager] UDP | Instance #{0} | Port: {1}
[InputSyncManager] ... bind UDP port {0}: {1}
[InputSyncManager] ... Fixed Master ... instance ... active ... #{0}
[InputSyncManager] Resize ... {0}x{1} (ratio: {2:F2})
```

Some Vietnamese characters are not preserved cleanly by ASCII string extraction, so only intact semantic fragments are quoted here.

These strings prove the implementation knows about:

- per-instance identity;
- a fixed-master mode and a focus-based fallback/mode;
- sync enable state;
- sync groups;
- UDP transport/port binding;
- active/inactive instance guards;
- window resize/aspect ratio handling.

This makes window/process/session state part of the diagnostic surface, not just CPU architecture.

---

## 8. InputRecorder evidence

Metadata exposes:

```text
InputRecorder
StartRecording
StartPlayback
startRecordingTime
```

and runtime messages:

```text
[InputRecorder] Recording...
[InputRecorder] Saved: {0} ({1} events)
[InputRecorder] Playing: {0} ({1} events, {2:F1}s)
[InputRecorder] Playback stopped
```

This matches the separate launcher evidence for recording/playback controls and strongly suggests the shipped PC stack was designed for deterministic/replayable input events across instances.

Do not infer the serialized event schema until `RecordedEvent` fields and the corresponding save/load path are explicitly mapped.

---

## 9. Launcher bridge relationship

The game metadata exposes:

```text
LauncherAutoLoginState
LauncherControlBridge
LauncherControlMessageDto
LauncherRoleItemDto
```

The launcher binary/PDB separately exposes functions such as:

```text
GetSelectedClientProcessIds
SendAutoLoginConfigAsync
SetSyncEnabledAsync
SetMasterAsync
SetSyncGroupAsync
RequestSyncStatesAsync
RequestScriptListAsync
StartRecordingAsync
StopRecordingAsync
StartPlaybackForProcessAsync
StopPlaybackForProcessAsync
```

This is mutually reinforcing evidence for a real launcher-to-game control channel.

Safe architecture conclusion:

```text
Launcher
 -> sends process/session/sync configuration
 -> per-game LauncherControlBridge / SyncBootstrap receives/applies it
 -> InputSyncManager handles per-instance input synchronization
```

The exact IPC framing/transport for launcher control is **not** established by this document and must not be invented.

---

## 10. Why a same-client machine can still fail `TryClickUI`

If these two hashes match:

```text
GameAssembly.dll
4c98c9934bc4260efa64f5492c58e0c5104c89359f0126e7cd402feb381fe3c7

global-metadata.dat
d199498dad7d3139e4c09f6742f4645bfc2a33c465e3d259196931199f6ee6a8
```

then the class/method metadata exists in both installations. A failure such as:

```text
cannot resolve InputSyncManager press/release/drag-state or Unity Screen
```

should be decomposed instead of summarized as “client khác”.

High-value failure classes are:

### A. Resolver brittleness

- relying on an unstable offset/RVA instead of semantic metadata;
- exact-name lookup fails because of namespace/nested-type assumptions;
- method overload/signature expectation is wrong;
- wrong image/assembly selected;
- stale cached pointer after a process/world reload.

### B. Initialization timing

- `SyncBootstrap.AutoInit` has not completed;
- registry/input module not yet ready;
- UI/EventSystem not ready;
- tool resolves during startup/map transition.

### C. Screen/window coordinate assumptions

- game window size/aspect differs;
- DPI scaling differs;
- client resize state differs;
- coordinate origin/Unity screen conversion differs;
- target RectTransform is not in a hittable state.

The presence of `WindowAspectLocker` and resize-ratio logging makes this class especially important.

### D. Pointer/drag lifecycle mismatch

- press state resolved but drag target/state not;
- stale `_uiDragging` / `_uiDragTarget` / `_uiDragData`;
- release/end-drag path omitted;
- hit-test finds geometry but not the expected interactive component.

### E. Process/session identity

- tool attaches to the wrong PID;
- instance registry state differs;
- selected master/group state differs;
- inactive instance guard refuses an operation.

### F. Graphics/input environment

GPU/backend/window mode can alter geometry/event timing or screen conversion. CPU model alone does not explain missing metadata symbols. A Xeon-specific theory therefore needs direct evidence before being promoted above resolver/window/runtime-state causes.

---

## 11. Recommended resolver strategy

For future hidden-click work, prefer a semantic and fail-closed chain:

```text
1. Verify exact snapshot hash
2. Resolve Assembly-CSharp image
3. Resolve type by namespace/name, not hardcoded absolute pointer
4. Resolve method by exact name + parameter count/type when available
5. Validate runtime object/static state
6. Validate Unity UI/EventSystem/Screen prerequisites
7. Resolve target/hit-test
8. Perform exactly one semantic click/input action
9. Complete required release/drag cleanup
10. Prove UI state changed
11. Re-scan before next mutation
```

Never silently fall back from a failed internal resolver to a random OS foreground click. That can hide the real failure and mutate the wrong client.

---

## 12. Highest-value next targeted reverse work

This archive has narrowed the remaining unknowns. The next useful reverse work is **not another broad GameAssembly scan**.

Priority order:

1. map declaring type + exact signature for `TryClickUI`;
2. map `FramePressState` and release-state counterpart(s);
3. map `EndUIDrag`, `CancelUIDragState`, `ResetUIDragState` signatures;
4. identify exact Unity `Screen`/RectTransform conversion helper used by `TryClickUI`;
5. map `PendingMessage` and `SyncInput` fields only if UDP/input mirroring is being implemented;
6. map `RecordedEvent` fields only if record/playback is needed;
7. map launcher bridge transport only if launcher-driven control is needed.

For a direct `UIButton.HandleClickEvent()` semantic callback, research the UIButton path separately from coordinate-based `TryClickUI`; the two may provide different reliability tradeoffs.

---

## 13. Evidence labels

### VERIFIED

- exact frozen snapshot identity;
- `PCSysnc` source paths listed above;
- type/name strings listed above;
- `SyncBootstrap.AutoInit` runtime initializer entry;
- `TryClickUI`, drag-state names, `UIButton`, `HandleClickEvent` existence;
- InputSync runtime log templates for master/group/UDP/resize;
- InputRecorder record/playback strings;
- launcher multi-instance/sync/record-playback controls exist.

### STRONG INFERENCE

- these components form one official PC multi-instance synchronization/control stack;
- robust hidden click requires coherent pointer/drag lifecycle rather than a press-only primitive;
- same hashes make resolver/runtime/window-state problems more likely than a missing client symbol.

### NOT YET VERIFIED

- exact native addresses/RVAs for these methods;
- exact method signatures and parameter order;
- exact event wire format;
- exact `TryClickUI -> UIButton.HandleClickEvent` call graph;
- exact Unity Screen conversion chain;
- exact reason a particular machine fails without runtime diagnostics from that machine.

This boundary must remain explicit so future implementations do not turn static string evidence into fabricated ABI assumptions.
