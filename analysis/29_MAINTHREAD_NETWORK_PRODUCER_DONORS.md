# MainThread producer donors — TCPGame/TCPLogin marshal callbacks through Execute(Action)

Status: **VERIFIED by metadata mapping + direct GameAssembly disassembly.**

This document answers an important question left after resolving the dispatcher consumer: **does the game itself actually use `MainThread.Execute(Action)` to marshal work originating outside the Unity Update path?** Yes.

## All direct xrefs found to `MainThread.Execute`

Direct static xrefs in the frozen GameAssembly resolve to four network callback methods:

### `FGStudio.Engine.Network.TCPGame`

- `SocketCommandHandler` — RVA `0x5DD560`, token RID `0x26C3`
- `SocketEventReportHandler` — RVA `0x5DD660`, token RID `0x26C2`

### `FGStudio.Engine.Network.TCPLogin`

- `SocketCommandHandler` — RVA `0x5DE7E0`, token RID `0x26F6`
- `SocketEventReportHandler` — RVA `0x5DE8F0`, token RID `0x26F5`.

Each path ultimately tail-calls/jumps to:

`MainThread.Execute(System.Action)` RVA `0x601250`.

This is highly meaningful: network/socket callbacks are a natural producer context that may not be the Unity frame thread, and the shipped client deliberately converts their work into `System.Action` objects and passes them through the MainThread queue.

## Exact generated pattern: `TCPGame.SocketCommandHandler`

The native method at RVA `0x5DD560` follows the standard IL2CPP closure/delegate construction pattern.

High-level reconstruction:

```text
initialize metadata for:
  display-class / closure type
  System.Action
  callback method metadata

closure = new compiler-generated display-class
closure..ctor()
closure.<captured command data> = incoming argument

mainThread = MainThread.Instance

action = new System.Action
System.Action..ctor(
    target = closure,
    method = compiler-generated closure callback
)

mainThread.Execute(action)
```

Direct native evidence includes:

- allocation of a compiler-generated object;
- store of the captured reference around closure offset `+0x10`;
- IL2CPP GC write-barrier call after capture assignment;
- read of `MainThread` static Instance through its TypeInfo static-field storage;
- allocation of `System.Action`;
- delegate-constructor call around VA `0x18049F810` with closure as target, callback pointer/metadata as the method argument and null MethodInfo tail argument;
- final tail jump to `0x180601250` (`MainThread.Execute`).

## `SocketEventReportHandler` captures multiple values

The event-report variant allocates a display-class and stores multiple incoming values before constructing the Action. Observed capture stores include fields around:

- `+0x10` — scalar/event value;
- `+0x18` — captured reference;
- `+0x20` — captured reference/object.

GC write barriers are emitted for captured managed references.

It then constructs `System.Action` and sends it through the same `MainThread.Execute` path.

## TCPLogin repeats the same design

`TCPLogin.SocketCommandHandler` and `TCPLogin.SocketEventReportHandler` use the same fundamental pattern and are the other direct Execute xrefs found in the module.

Therefore this is not an accidental one-off helper: it is the intended game architecture for moving network-originated work into Unity's MainThread queue.

## Useful snapshot-native helpers observed

The generated donor code reveals several internal helper roles:

- runtime-metadata initialization helper around `0x180358A50`;
- generated object-allocation helper around `0x180358CA0` (which dispatches into the IL2CPP allocation implementation);
- managed reference write-barrier helper around `0x180357DA0`;
- `System.Action` constructor implementation used by these donors around `0x18049F810`;
- `MainThread.Execute` at `0x180601250`.

These are **historic frozen-snapshot addresses**, not preferred production API identities. Use them as reverse evidence/debug hints. Future code should resolve types/methods semantically whenever practical.

## Critical external-bridge lesson

Do not manually forge a fake `System.Action` memory block by copying offsets from one delegate object. The shipped compiler-generated path does more than fill a few pointers:

1. creates a legitimate managed object;
2. constructs a legitimate closure target when parameters must be captured;
3. uses IL2CPP GC write barriers for managed-reference captures;
4. constructs the delegate through `System.Action..ctor`;
5. keeps object/type/runtime metadata consistent;
6. only then calls `MainThread.Execute`.

A safe external bridge should preserve these managed-runtime semantics rather than treating Action as an unmanaged callback struct.

## Two implementation strategies suggested by the donor

### Strategy A — managed-compatible bridge callback

Create/root a legitimate managed target + `System.Action` using IL2CPP allocation/delegate construction, with the callback thunk obeying the exact IL2CPP delegate ABI. Then enqueue through `MainThread.Execute`.

This is closest to the game's own producer path but still needs one live lifetime/GC proof.

### Strategy B — reuse an existing game-owned producer/helper when semantics fit

If an already-existing game/Lua helper schedules exactly the required work, prefer invoking that semantic helper rather than constructing a custom delegate solely to reproduce it.

Do not contort a network handler into an unrelated action; the donor is primarily evidence for construction/marshalling semantics.

## What is now VERIFIED vs still pending

### VERIFIED

- `Execute(Action)` is a real producer API.
- the game itself calls it from TCPGame/TCPLogin callback handlers.
- the game constructs legitimate `System.Action` delegates before enqueueing.
- captured managed references go through write barriers.
- MainThread Update later dequeues/invokes those Actions (see `analysis/21_MAIN_THREAD_DISPATCHER.md`).

### Pending live external proof

- exact external mechanism chosen to create/root the callback Action;
- callback ABI for a custom external bridge thunk if Strategy A is used;
- GC/lifetime behavior across enqueue-to-next-Update window;
- producer thread vs Unity callback thread ID observation.

## Architectural conclusion

The complete shipped pattern is now evidenced on both sides:

```text
NETWORK PRODUCER
  TCPGame/TCPLogin callback
      -> managed closure
      -> System.Action
      -> MainThread.Execute(Action)

QUEUE/CONSUMER
  ConcurrentQueue<Action>
      -> Unity Update
      -> DoExecuteWorks
      -> TryDequeue
      -> Action.Invoke
```

This is the strongest available donor for the external tool's action bridge and further supports rejecting arbitrary-thread direct gameplay invocation as the canonical architecture.
