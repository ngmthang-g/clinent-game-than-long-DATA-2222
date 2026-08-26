# 43 — InputSync exact signatures, native RVAs and UI pointer/drag lifecycle

Status: **VERIFIED for the frozen client snapshot** from metadata v39 plus native `GameAssembly.dll` disassembly. RVAs are valid only for the exact hashes in `CLIENT_MANIFEST.md`; future client builds must re-resolve by metadata/token rather than reuse these addresses blindly.

Machine-readable shortlist: `database/PC_INPUTSYNC_METHODS.csv`.

## 1. Important corrections to the earlier static-name audit

Several names seen near the PC sync strings do **not** belong to `InputSyncManager`.

Exact declaring types are:

- `FramePressState` = nested enum `UnityEngine.EventSystems.PointerEventData+FramePressState`.
- `PointerInputModule.StateForMouseButton(int buttonId) -> FramePressState`, token `0x0600072F` in `UnityEngine.UI.dll`.
- `PointerInputModule.GetLastPointerEventData(int id) -> PointerEventData`, token `0x06000732` in `UnityEngine.UI.dll`.
- `Joystick.InjectSyncInput(Vector2 dir) -> void`, token `0x06000024` in `Assembly-CSharp-firstpass.dll`.
- `InstanceRegistry.SetSyncState(bool isIn)`, `GetSyncGroupId()` and `SetSyncGroup(int)` belong to `InstanceRegistry`, not `InputSyncManager`.

This distinction is critical for resolver design. Do not scan `InputSyncManager` for `FramePressState`, `GetLastPointerEventData`, `InjectSyncInput` or `SetSyncState`.

## 2. Exact `InputSyncManager` UI methods

Frozen `Assembly-CSharp.dll` metadata gives:

| Method | Token | Static | RVA |
|---|---:|---:|---:|
| `ConvertPos(int masterX, int masterY, int masterW, int masterH) -> Vector2` | `0x06000060` | yes | `0x004FFE20` |
| `ParseAndInject(string evt) -> void` | `0x06000061` | no | `0x00500590` |
| `TryClickUI(int btn, Vector2 screenPos) -> void` | `0x06000066` | no | `0x00502E40` |
| `UpdateUIDrag(Vector2 screenPos) -> void` | `0x06000067` | no | `0x00503710` |
| `EndUIDrag(Vector2 screenPos) -> void` | `0x06000068` | no | `0x004FFEA0` |
| `CancelUIDragState() -> void` | `0x06000069` | no | `0x004FE470` |
| `ResetUIDragState() -> void` | `0x0600006A` | no | `0x00501D10` |

The `Assembly-CSharp` CodeGenModule contains 12,688 method pointers; token RID indexes resolve the rows above to those exact native pointers in this snapshot.

## 3. Native Windows-x64 ABI actually observed

`TryClickUI` begins by consuming:

```text
RCX = InputSyncManager* this
EDX = int btn
R8  = Vector2 screenPos packed as two 32-bit floats in one 64-bit value
R9  = hidden RuntimeMethod/MethodInfo pointer
```

The shipped `ParseAndInject` caller explicitly zeroes `R9` before the direct call. Therefore a native bridge must not model this as a simple two-argument free function.

`UpdateUIDrag` / `EndUIDrag` use:

```text
RCX = this
RDX = packed Vector2
R8  = hidden method pointer; shipped caller passes zero
```

`CancelUIDragState` uses `RCX=this`; shipped internal callers zero the hidden next argument register.

`ConvertPos` is static. Its four managed integer arguments occupy `RCX/EDX/R8D/R9D`; it returns the two-float `Vector2` packed in `RAX` in this generated build.

These ABI facts are stronger than guessing from C#-style signatures alone.

## 4. `ConvertPos` is the screen-size normalization bridge

Native arithmetic verifies the conversion shape:

```text
x = currentScreenWidth  * masterX / masterW
y = currentScreenHeight * masterY / masterH
return Vector2(x, y)
```

This explains why a same-hash client can fail on another machine when window size, aspect ratio or DPI/screen state differs. A tool that injects master-space coordinates without passing through the same conversion contract can hit the wrong UI even though every symbol resolves correctly.

## 5. Exact `ParseAndInject` call graph relevant to UI input

Direct native calls from `InputSyncManager.ParseAndInject` include:

```text
ConvertPos        at caller RVA 0x005007B5 and 0x00500F22
SyncInput.InjectMousePos
EndUIDrag         at caller RVA 0x005008B2
TryClickUI        at caller RVA 0x00500966
UpdateUIDrag      at caller RVA 0x00500F58
```

Therefore the official path is not "just click at X/Y". The synchronized event parser converts coordinates, updates simulated mouse position and dispatches different UI operations according to event state.

No direct native call from `TryClickUI` to `FGStudio.LuaSystem.GUI.UIButton.HandleClickEvent()` was found. `TryClickUI` follows the Unity EventSystem/pointer route; direct `UIButton.HandleClickEvent()` is a separate semantic callback path and should be treated separately by the tool.

## 6. What `TryClickUI` actually initializes

Native writes inside `TryClickUI` show a fresh/working `PointerEventData` being populated with:

- `position.x/y` from `screenPos`;
- `pointerId = -1` initially;
- `button` mapping:
  - `btn == 0` -> Left;
  - `btn == 1` -> Right;
  - any other value -> Middle.

The method performs EventSystem/raycast-style target work and marks the simulated UI-click state. On its left-button path it stores persistent drag state for later update/end processing.

This is why a resolver that only finds a press primitive is incomplete: the client maintains a real pointer/drag lifecycle.

## 7. Exact persistent drag fields and object offsets

Metadata field identities:

- `_uiDragging` — field token `0x0400002D`
- `_uiDragTarget` — `0x0400002E`
- `_uiDragData` — `0x0400002F`

Native accesses on the frozen `InputSyncManager` object verify:

```text
this + 0x78 -> _uiDragging
this + 0x80 -> _uiDragTarget
this + 0x88 -> _uiDragData
```

After a qualifying `TryClickUI` left-button path, the binary writes:

```text
_uiDragging = true
_uiDragTarget = resolved target
_uiDragData = PointerEventData
```

`UpdateUIDrag` first guards `_uiDragging != 0` and `_uiDragData != null` before updating the pointer/drag path.

## 8. End/cancel/reset semantics

`EndUIDrag(Vector2)`:

1. requires active drag + non-null drag data;
2. updates pointer position;
3. performs the relevant pointer/end/drag EventSystem dispatches;
4. always clears `_uiDragging`, `_uiDragTarget`, `_uiDragData` before returning from the normal/cold cleanup paths.

`CancelUIDragState()` similarly attempts the appropriate cancellation/end event work when state exists, then clears the same three fields.

`ResetUIDragState()` is the minimal state clear:

```text
_uiDragging = false
_uiDragTarget = null
_uiDragData = null
```

Direct xrefs verify `CancelUIDragState()` is called by both:

- `ClearSyncRuntimeState()`
- `ReleaseInjectedInputState()`

So session/input cleanup explicitly includes UI drag cleanup; stale drag state is not an optional detail.

## 9. Related exact semantic methods

`SyncInput` in `Assembly-CSharp.dll`:

- `InjectMouseDown(int btn)` token `0x060000C7`, RVA `0x0050E550`
- `InjectMouseUp(int btn)` token `0x060000C8`, RVA `0x0050E680`
- `InjectMousePos(Vector2 pos)` token `0x060000C9`, RVA `0x0050E5F0`
- `SetClickedUI(bool value)` token `0x060000CD`, RVA `0x0050E790`

`UIButton`:

- `HandleClickEvent()` token `0x060003DC`, RVA `0x0052D140`
- `HandlePointerUp(PointerEventData)` token `0x060003DE`, RVA `0x0052D3F0`
- `HandlePointerDown(PointerEventData)` token `0x060003DF`, RVA `0x0052D270`

`UIDragableObject`:

- `IsRectTransformInsideScreen(RectTransform)` token `0x06002C6A`, RVA `0x0060A3E0`
- `OnDrag(PointerEventData)` `0x06002C6B`, RVA `0x0060A630`
- `OnBeginDrag(PointerEventData)` `0x06002C6C`, RVA `0x0060A5D0`
- `OnEndDrag(PointerEventData)` `0x06002C6D`, RVA `0x0060A7F0`

## 10. Resolver contract for future tool work

For this exact snapshot, a robust resolver can validate both semantic metadata and native address:

```text
verify GameAssembly + metadata hashes
 -> Assembly-CSharp image
 -> InputSyncManager type
 -> token/signature check
 -> resolve current method pointer
 -> verify object/bootstrap readiness
 -> ConvertPos when source coordinates are master-space
 -> TryClickUI / UpdateUIDrag / EndUIDrag according to the event lifecycle
 -> prove UI state change
 -> Cancel/Reset on abort/session teardown
```

Prefer token + declaring type + parameter signature over a hardcoded RVA. RVA is a frozen-snapshot cross-check, not the primary identity.

If another PC has the same hashes and fails, prioritize:

1. wrong image/type/method resolver;
2. bootstrap/init timing;
3. wrong PID/instance/master/group state;
4. screen/window/DPI conversion;
5. stale `_uiDragging/_uiDragTarget/_uiDragData` lifecycle;
6. EventSystem/target readiness.

A Xeon CPU model by itself does not explain a missing method that is proven present in the same binary/metadata snapshot.

## 11. What remains runtime-only

Static reverse work for the core hidden-click signature/lifecycle is now effectively closed for this frozen build.

Remaining validation belongs in the production tool/runtime:

- resolve the same tokens on each PID;
- obtain the correct live `InputSyncManager` instance after bootstrap;
- execute a harmless target and verify UI transition;
- verify coordinate behavior under the target machine's DPI/window configuration;
- verify abort/release leaves drag state cleared.

Do not broad-reverse GameAssembly again unless a future client hash changes or a genuinely new InputSync semantic contract is required.
