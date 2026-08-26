# 37 — PC InputSync / hidden UI click static evidence

Status: **VERIFIED static discovery for the frozen client.** Exact declaring types, signatures, tokens, native RVAs, ABI and UI drag lifecycle are now canonical in `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md` and `database/PC_INPUTSYNC_METHODS.csv`.

This document remains the compact discovery/background layer. Do not use old string proximity as a declaring-type assumption.

## 1. Frozen snapshot

Use the exact hashes in `CLIENT_MANIFEST.md` / `database/CLIENT_FILE_MANIFEST_SHA256.csv` before applying snapshot-specific native addresses.

The client is Unity/IL2CPP and metadata exposes the project folder:

```text
Assets\Scripts\Game\Logic\PCSysnc\
```

The spelling `PCSysnc` is exact.

Relevant source paths include:

```text
InputRecorder.cs
InputSyncManager.cs
InstanceRegistry.cs
LauncherAutoLoginState.cs
LauncherControlBridge.cs
SyncBootstrap.cs
SyncInput.cs
SyncInputModule.cs
SyncOverlayUI.cs
UnityMainThreadDispatcher.cs
WindowAspectLocker.cs
```

UI-side paths include:

```text
Assets\Scripts\LuaSystem\GUI\Button\UIButton.cs
Assets\Scripts\Engine\Utilities\Unity\UI\UIDragableObject.cs
```

## 2. Startup / PC multi-instance evidence

`RuntimeInitializeOnLoads.json` contains:

```text
className = SyncBootstrap
methodName = AutoInit
```

So the PC sync stack is automatically initialized by the shipped client.

Runtime strings also verify:

- instance identity;
- fixed-master and focus-based behavior;
- sync groups;
- UDP transport/port binding;
- active-instance checks;
- resize/aspect handling;
- recording/playback.

The launcher/PDB independently exposes sync/master/group/record/playback controls, reinforcing that this is an official PC multi-instance subsystem rather than an invented external-input mechanism.

## 3. Correct ownership of important names

Earlier broad string discovery placed several names near the InputSync evidence but did not prove their declaring type. Exact metadata parsing now resolves them:

### `InputSyncManager`

Owns the core PC sync/UI methods including:

```text
SetSyncEnabled
SetSyncGroup
CaptureAndBroadcast
ParseAndInject
ConvertPos
TryClickUI
UpdateUIDrag
EndUIDrag
CancelUIDragState
ResetUIDragState
```

### `InstanceRegistry`

Owns:

```text
SetSyncState
GetSyncGroupId
SetSyncGroup
GetSyncPeers
```

### `SyncInput`

Owns simulated key/mouse state methods including:

```text
InjectKeyDown / InjectKeyUp
InjectMouseDown / InjectMouseUp
InjectMousePos
InjectScroll
SetClickedUI
GetMouseButtonDown / Up / Hold
```

### Unity EventSystem, not InputSyncManager

`FramePressState` is:

```text
UnityEngine.EventSystems.PointerEventData+FramePressState
```

`GetLastPointerEventData(int)` is declared by:

```text
UnityEngine.EventSystems.PointerInputModule
```

The same type also owns `StateForMouseButton`, `ShouldStartDrag`, `ProcessMove`, `ProcessDrag`.

### `Joystick`

`InjectSyncInput(Vector2)` belongs to `Joystick` in `Assembly-CSharp-firstpass.dll`, not `InputSyncManager`.

These corrections matter because a resolver that searches the wrong class can report a false "method missing" failure despite identical binaries.

## 4. UI state model

Exact native work is documented in analysis 43. High-level verified lifecycle is:

```text
Parse synchronized event
 -> convert source/master coordinates
 -> update simulated mouse position
 -> TryClickUI for UI press/click path
 -> maintain persistent PointerEventData/drag target when needed
 -> UpdateUIDrag while moving
 -> EndUIDrag on release
 -> CancelUIDragState on abort/session cleanup
 -> clear drag state
```

The frozen `InputSyncManager` object stores:

```text
_uiDragging  at +0x78
_uiDragTarget at +0x80
_uiDragData   at +0x88
```

Those offsets are snapshot-specific native evidence, not universal offsets for future builds.

## 5. UIButton is a separate semantic path

Metadata proves:

```text
FGStudio.LuaSystem.GUI.UIButton.HandleClickEvent()
HandlePointerDown(PointerEventData)
HandlePointerUp(PointerEventData)
```

Exact native call analysis does **not** show `TryClickUI` directly calling `UIButton.HandleClickEvent()`. `TryClickUI` follows the Unity EventSystem pointer/hit-test path, while direct `UIButton.HandleClickEvent()` is a separate semantic callback option.

Do not merge these into one assumed implementation.

## 6. Machine-specific failure diagnosis

When `GameAssembly.dll` and `global-metadata.dat` hashes match, a failure resolving/using hidden click should prioritize:

1. declaring type/image mismatch;
2. signature/parameter-count mismatch;
3. bootstrap/init timing;
4. wrong PID/instance/master/group;
5. window size/aspect/DPI/screen conversion;
6. EventSystem/UI readiness;
7. stale drag-state lifecycle;
8. cached pointers surviving process/world transitions.

CPU model alone is weak evidence. In particular, a Xeon does not remove metadata methods that are byte-identical in the same snapshot.

## 7. Canonical next read

For implementation or debugging, do not stop at this discovery note. Read:

1. `analysis/43_INPUT_SYNC_EXACT_SIGNATURES_AND_UI_LIFECYCLE.md`
2. `database/PC_INPUTSYNC_METHODS.csv`
3. `analysis/07_SUPPORT_MODULES_LAUNCHER.md` only when launcher/session control is actually relevant.

The core hidden-click signature/lifecycle static reverse is now considered **closed for this frozen snapshot**. Future work should be runtime integration proof unless client hashes change.
