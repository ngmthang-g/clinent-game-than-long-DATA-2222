# Runtime Buff schema / event model

Status: **VERIFIED from decrypted `BuffFrame.lua`, `BuffTooltip.lua`, `TCPCmdEventHandler.lua`.**

This is the strongest static evidence so far for implementing buff-aware automation without guessing from icons or HP alone.

## Local-player buff list

The stock UI calls:

`Game.GetBuffs()`

and iterates structured `buffData` objects.

Fields directly consumed by shipped Lua:

- `BuffID`
- `DurationTick`
- `Stack`.

`DurationTick` is explicitly documented by the Lua comments as milliseconds.

## Event-driven buff lifecycle

`TCPCmdEventHandler` handles:

- `G_TCPEventType.AddBuff = 15`
- `G_TCPEventType.UpdateBuff = 16`
- `G_TCPEventType.RemoveBuff = 17`.

### Add

The event data is a `dbBuffData` object and is passed to:

`BuffFrame:AddBuff(dbBuffData)`.

If the buff already exists, the UI updates its duration; otherwise it creates a new icon and stores it keyed by `BuffID`.

### Update

The UI updates:

- `dbBuffData.BuffID`
- `dbBuffData.DurationTick`
- `dbBuffData.Stack`.

### Remove

The event supplies the relevant BuffID and the corresponding icon/state is destroyed.

## Buff metadata / tooltip schema

`Game.GetBuffData(buffID)` returns a richer record used by `BuffTooltip`.

Fields directly accessed:

- `BuffID`
- `Level`
- `Stack`.

The tooltip determines display name/icon semantically:

- if `Game.GetItemType(BuffID) != "Undefined"`, use item name/icon;
- otherwise use `Game.GetSkillName(BuffID)` and `Game.GetSkillIcon(BuffID)`.

So a BuffID may semantically originate from an item or a skill.

## Buff properties

The UI calls:

`Game.GetBuffProperties(BuffID)`

and receives a list of attribute records.

At least the field:

- `attributeData.Type`

is directly accessed.

If any property has:

`Type == "magic_can_positive_remove"`

then the game exposes the positive-remove button.

Manual removal uses:

`Game.SendRemoveBuff(BuffID)`.

## Description generation

Buff properties are fed to:

`GF_GetSkillMagicAttributesDescription(attributes, level, ...)`

which means the same `MagicAtrributes` semantic layer used by skills is also used to describe buffs.

This gives future AI a route to build human-readable buff explanations from:

`BuffID -> Level -> GetBuffProperties -> magic attribute descriptions`.

## Exact buff state model suitable for a tool

A local immutable snapshot can contain:

```text
BuffID
Level                # from GetBuffData
DurationTick         # live buff list/event
Stack                # live buff list/event
Name                 # GetSkillName/GetItemName
SourceKind            # skill-like vs item-like semantic classification
Properties[]          # GetBuffProperties when needed
CanPositiveRemove     # property contains magic_can_positive_remove
LastObservedTick
```

Do not call `GetBuffProperties` for every buff on every frame unless needed; static properties can be cached by BuffID.

## Auto Buff state proof

For self-buff logic, the client already uses:

`Game.HasBuff(skillID)`.

For richer verification after a cast, prefer:

1. AddBuff/UpdateBuff event;
2. fresh `Game.GetBuffs()` containing expected BuffID;
3. `DurationTick` / `Stack` change;
4. only then fallback to cooldown/cast state if the beneficial skill does not produce a local-player buff.

This is much stronger than waiting a fixed number of milliseconds.

## Target buffs: current limitation

For other selected players/teammates, shipped UI explicitly exposes:

`Game.GetTargetBuffIcons(RoleID)`

which returns icon data used by `MainUI_OtherHeader`, `MainUI_PetHeader` and team UI.

The Lua source inspected so far does **not** prove a public structured `GetBuffs(targetRoleID)` equivalent with BuffID/Duration/Stack for arbitrary nearby players.

Therefore:

- local-player buff IDs/duration/stack are VERIFIED;
- target buff **icons** are VERIFIED;
- exact target BuffID/duration list remains a targeted runtime/API research item unless another source proves it.

Do not silently infer BuffID from an icon filename unless separately mapped.

## Relevance to Nga My Auto Buff

For healing spells, target HP changes can be direct state proof.

For persistent beneficial buffs:

- use exact target buff data if a structured target API is later found;
- otherwise combine successful cast/cooldown state with the strongest observable target state available;
- never spam repeated casts solely because icon parsing is uncertain.

## Removal safety

`Game.SendRemoveBuff(BuffID)` is a semantic game action, but only use it when the buff's properties explicitly mark it removable or the user intentionally requested removal. Do not mass-remove unknown buffs.
