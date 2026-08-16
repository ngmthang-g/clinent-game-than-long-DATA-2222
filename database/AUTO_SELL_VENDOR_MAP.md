# Auto Sell Vendor Map — automation-focused NPC service candidates

Purpose: keep only vendor/NPC knowledge useful to Auto Sell. This is **not** a general NPC encyclopedia.

Evidence labels used here:

- **VERIFIED STATIC IDENTITY** — NPC ID/name/map/ResName are confirmed from the frozen Config/AutoPath database.
- **USER-REPORTED SERVICE** — the user has identified the NPC in gameplay as a selling destination, but the exact GameDialog/NPCShop service path has not yet been captured into canonical runtime evidence.
- **PROBABLE SERVICE CANDIDATE** — inferred from repeated merchant/blacksmith ResName archetype only.
- **RUNTIME VERIFIED SELL VENDOR** — reserve this status for a repeatable runtime proof that the NPC opens a normal sell-capable `NPCShop` (`IsGuildShop == false`) and exposes valid current `NpcShopID` / `ShopID`.

Never promote USER-REPORTED/PROBABLE to runtime VERIFIED without evidence.

---

# 1. Lâu Lan (MapID 5) — highest current Auto Sell priority

## NPC 328 — Ba Nhĩ

```text
NPC_ID   = 328
Name     = Ba Nhĩ
ResName  = ALaBoNanRen2
MapID    = 5
MapName  = Lâu Lan
```

Status:

- identity: **VERIFIED STATIC IDENTITY**;
- sell service: **USER-REPORTED SERVICE**;
- exact dialog/shop path: **PENDING RUNTIME CAPTURE**.

Important: `ResName=ALaBoNanRen2` is a generic character archetype and does not itself prove merchant service. The service claim comes from user gameplay knowledge, not from the ResName.

## NPC 373 — Mã Kiêu Minh

```text
NPC_ID   = 373
Name     = Mã Kiêu Minh
ResName  = ZhanDouXiaoYaoDiZi
MapID    = 5
MapName  = Lâu Lan
```

Status:

- identity: **VERIFIED STATIC IDENTITY**;
- sell service: **USER-REPORTED SERVICE**;
- exact dialog/shop path: **PENDING RUNTIME CAPTURE**.

Important: `ResName=ZhanDouXiaoYaoDiZi` is not a merchant archetype, so do not infer service from model name. Keep the service claim explicitly separated as user-reported until runtime shop data proves it.

## NPC 341 — Hiệp Hàng

```text
NPC_ID   = 341
Name     = Hiệp Hàng
ResName  = npcXiYuTuoDuiShangRen
MapID    = 5
MapName  = Lâu Lan
```

Status:

- identity: **VERIFIED STATIC IDENTITY**;
- service: **PROBABLE SERVICE CANDIDATE**.

Reason: ResName contains `ShangRen` (merchant) and is a caravan-merchant archetype. This is a strong discovery candidate but not proof that the current server exposes a normal sell-capable NPCShop.

## NPC 398 — Chu Thập Tam

```text
NPC_ID   = 398
Name     = Chu Thập Tam
ResName  = TieJiang
MapID    = 5
MapName  = Lâu Lan
```

Status:

- identity: **VERIFIED STATIC IDENTITY**;
- service: **PROBABLE BLACKSMITH/REPAIR CANDIDATE**.

A blacksmith may expose equipment/repair/shop services, but do not assume normal selling without current runtime NPCShop evidence.

---

# 2. Candidate priority for Auto Sell testing

For Lâu Lan, recommended evidence-collection order is:

```text
1. Ba Nhĩ (328)       — user-reported selling destination
2. Mã Kiêu Minh (373) — user-reported selling destination
3. Hiệp Hàng (341)    — strongest static merchant archetype
4. Chu Thập Tam (398) — blacksmith/service fallback candidate
```

This order is for **runtime verification**, not a claim that 328 is intrinsically a better merchant than 373.

---

# 3. Exact runtime promotion test

To promote one candidate to `RUNTIME VERIFIED SELL VENDOR`:

```text
fresh MapSnapshot confirms expected MapID
 -> GoToNPC(mapID,npcID)
 -> wait/inspect current GameDialog if present
 -> choose the current trade/shop selection by visible text, not a hardcoded selection ID
 -> wait inbound CMD_NPC_SHOP_DATA = 200034
 -> capture current NPCShop data
 -> require IsGuildShop == false
 -> capture NpcShopID + ShopID
 -> optionally send ONE safe sell request for an explicitly disposable test item
 -> verify RemoveItem / UpdateItemsList / money/shop state
```

If the NPC opens `NPCShop` directly without an intermediate GameDialog, the dialog step is simply absent.

Do not mark a vendor verified merely because clicking the NPC opens some UI.

---

# 4. Coordinates policy

Do **not** hardcode old/manual NPC coordinates as canonical vendor identity.

Use:

```text
Game.GetNPCPosition(npcID)
```

and route through the built-in `GoToNPC`/`Game.GoTo` mechanism.

Reason:

- static/config coordinate systems may differ from live world units;
- map/server content may move service instances;
- runtime semantic position is the strongest action-time source already exposed by the client.

---

# 5. Vendor profile stored by the external tool

Once runtime verified, a per-map vendor profile should contain only stable semantic information:

```text
VendorProfile
  MapID
  NpcID
  DisplayName
  ServiceStatus
  LastRuntimeVerifiedAt
  DialogMatchText optional
  ShopDirectOrDialog
```

Do **not** persist `NpcShopID`, `ShopID`, live NPC RoleID or GameDialog selection ID as permanent constants unless repeated evidence proves they are stable. Prefer reading them fresh from current runtime state.

---

# 6. Selection policy for multiple vendors

If more than one vendor on a map is runtime verified, the tool may select by user/config policy:

```text
PreferredVendorNpcID
fallback verified vendors
shortest current route / user priority
```

Do not automatically choose a statically inferred merchant over a user-selected verified destination.

---

# 7. Cross-map expansion rule

Do not map every merchant in all 193 maps.

Only add another map when:

- the user actually configures a Train spot there; or
- Auto Sell needs a fallback route from that map.

For each new map, keep the same evidence ladder:

```text
static identity
 -> user report / semantic archetype candidate
 -> runtime GameDialog/NPCShop proof
 -> verified vendor profile
```

This keeps the knowledge base small and directly useful to the Auto tool.

Canonical supporting docs:

- `database/NPC_SERVICE_CANDIDATES.md`
- `database/npcs/NPCS_*.csv`
- `features/AUTO_SELL.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`
- `analysis/22_MAP_MINIMAP_RUNTIME.md`
- `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`
