# Auto Runtime Proof Queue — only unresolved evidence worth collecting

Purpose: prevent future AI from broad-reversing solved client areas. This file contains only **runtime/server proofs that are still genuinely missing for the Auto Thần Long tool**.

Do not add speculative research here. A proof enters this queue only when the static/Lua/native architecture is already understood and one live behavior remains.

Priority labels:

- **P0** — blocks many mutable auto features.
- **P1** — blocks one important feature.
- **P2** — optional enhancement only if a concrete implementation needs it.

---

# P0-1 — External managed Action -> MainThread live callback

Status: **IMPLEMENTATION PROOF ONLY**.

Already solved statically:

```text
MainThread.Execute(Action)
 -> ConcurrentQueue<Action>
 -> Unity Update
 -> DoExecuteWorks
 -> Action.Invoke
```

Game-owned TCP producer handlers already prove valid managed Action construction/use.

What remains:

```text
external tool constructs + roots one valid managed System.Action
 -> MainThread.Execute(Action)
 -> return without blocking Unity thread
 -> next Update invokes callback
 -> external tool observes harmless state change
```

Canonical harmless proof donor:

```text
System.Threading.CancellationTokenSource
Cancel()
IsCancellationRequested false -> true
```

PASS evidence:

- callback executes through the MainThread queue;
- Unity/game remains stable;
- object/delegate lifetime is valid;
- no arbitrary-thread Unity/Lua call is required.

Do not re-reverse dispatcher internals if this fails. Debug construction/rooting/lifetime/protocol first.

Canonical docs:

- `analysis/21_MAIN_THREAD_DISPATCHER.md`
- `analysis/29_MAINTHREAD_NETWORK_PRODUCER_DONORS.md`
- `analysis/30_EXTERNAL_ACTION_BRIDGE_BLUEPRINT.md`
- `contracts/MAINTHREAD_BRIDGE_V1.md`.

---

# P1-1 — Nga My beneficial skill on non-team PeacePlayer

Status: **SERVER ACCEPTANCE UNKNOWN FOR SPECIFIC RELATIONSHIPS/SKILLS**.

Already solved:

- nearby PeacePlayer RoleID/HP/MaxHP/name/faction/guild;
- SelectTarget/ChaseTarget/cast semantic path;
- cooldown/progress guards;
- exact Nga My IDs including corrected 407/423 identity.

Test only the skill(s) the production tool will actually use.

Minimum proof sequence:

```text
fresh PeacePlayer target
 -> record RoleID + HP/MaxHP + team/guild relationship
 -> verify skill owned/ready/condition
 -> select/chase if required
 -> issue ONE RequestUsingSkillWithTarget(skillID,RoleID)
 -> observe server/runtime result
```

PASS evidence for heal-type skill may include:

- target HP increases consistently;
- cooldown/progress changes consistently with accepted cast;
- no rejection state/message.

For persistent buff skill, target buff icon/state or other semantic response may be required.

Record separately for:

```text
same team
same guild but not team
unrelated PeacePlayer
self where applicable
```

Do not assume acceptance from the `PeacePlayer` target type alone; server rules are authoritative.

Canonical docs:

- `analysis/14_NEARBY_ENTITY_UI_SCHEMA.md`
- `analysis/15_AUTO_RECOVERY_NGAMY_ENGINE.md`
- `analysis/18_SKILLBAR_COOLDOWN_QUICKSKILLS.md`
- `features/AUTO_BUFF.md`.

---

# P1-2 — NPC Trị liệu exact live dialog sequence

Status: **DYNAMIC SERVER DIALOG UNKNOWN**.

Already solved:

```text
NPC 339 = Đỗ Thanh Đằng
MapID 5 = Lâu Lan
ResName = LangZhong1
GoToNPC / GetNPCPosition / ClickNPC
GameDialog.Selections[selectionID] = visibleText
CMD_SHOW_GAMEDIALOG = 100007
payload = selectionID:SelectedItemID
```

Required capture:

```text
before interaction: HP + money + current dialog generation
 -> GoToNPC(5,339)
 -> interact
 -> copy ALL current GameDialog selections exactly
 -> identify visible Trị liệu/service text
 -> record current selectionID
 -> send current selection
 -> capture any second confirmation dialog
 -> if confirmation exists, record its current text/selectionID
 -> observe HP/money/dialog result
```

PASS evidence:

- service text and dynamic selection path captured;
- any confirmation step captured;
- HP/result changes consistently;
- no fixed/global selection ID is assumed.

If NPC 339 does not expose the desired service on the live server, test another `LangZhong` candidate only then.

Canonical docs:

- `features/AUTO_HEAL_NPC.md`
- `database/NPC_SERVICE_CANDIDATES.md`
- `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`.

---

# P1-3 — Lâu Lan Auto Sell vendor promotion

Status: **STATIC IDs + USER-REPORTED DESTINATIONS KNOWN; EXACT SHOP PATH NOT CAPTURED**.

Current priority candidates:

```text
328 Ba Nhĩ       — USER-REPORTED selling destination
373 Mã Kiêu Minh — USER-REPORTED selling destination
341 Hiệp Hàng    — PROBABLE merchant archetype
398 Chu Thập Tam — PROBABLE blacksmith/service candidate
```

Verification order should start with 328/373 because gameplay knowledge is stronger than model-name inference.

Proof sequence:

```text
GoToNPC(5,npcID)
 -> interact
 -> if GameDialog appears, copy selections and choose current shop/trade service
 -> wait CMD_NPC_SHOP_DATA=200034
 -> capture current NpcShopID + ShopID + IsGuildShop
 -> require IsGuildShop == false
```

Optional transaction proof with one explicitly disposable item:

```text
fresh item instance ID
 -> 200036 instanceID:NpcShopID:ShopID
 -> RemoveItem / UpdateItemsList / money-shop evidence
```

Promotion result:

```text
RUNTIME VERIFIED SELL VENDOR
```

Do not persist current `NpcShopID`, `ShopID` or dialog selection ID as eternal constants without repeated stability evidence.

Canonical docs:

- `database/AUTO_SELL_VENDOR_MAP.md`
- `features/AUTO_SELL.md`
- `analysis/20_BAG_GRID_SHOP_UI_RUNTIME.md`.

---

# P2-1 — Arbitrary non-team PeacePlayer Position / death state

Only prove this if the chosen Auto Buff implementation cannot work cleanly from current target/chase APIs and fresh PeacePlayer records.

Do not research it merely because a richer Entity Scanner would look nicer.

Already known:

```text
PeacePlayer RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/TeamRank
SelectedTarget HPPercent/type/identity
team members have exact map/backup position and nearby precise position
```

Need Position/death only when a concrete range/eligibility policy cannot be implemented without it.

---

# P2-2 — Absolute live HP/MaxHP for every unselected monster

Basic Train does not require this.

Already solved target discovery fields:

```text
Type
IsDeath
RoleID
ResID
Position
```

Selected target has `HPPercent`.

Only prove absolute HP/MaxHP for all nearby unselected monsters if a future policy explicitly needs comparisons such as lowest absolute HP or boss-health telemetry.

---

# P2-3 — Rich arbitrary-target BuffID/duration list

Local buff list is fully structured (`BuffID, DurationTick, Stack`). Other targets currently have verified target buff icons.

Only pursue richer arbitrary-target BuffID/duration data if Auto Buff cannot avoid spam/recast reliably using:

- target HP change;
- cast/cooldown/progress evidence;
- target buff icons;
- known skill timing/policy.

---

# Closed gaps — never re-add without contradictory evidence

The following are **not** research gaps anymore:

```text
Auto Train semantic start/stop
nearby PeacePlayer identity + HP/MaxHP
bag free-space and item structured state
item instance ID vs template ItemID
exact Auto Sell packet/payload
Quick Sell semantics
Revive/Đầu thai packet/types
GameDialog dynamic selection architecture
Game.GetNPCPosition / GoToNPC route principle
Nga My 406/407/408/423/424 identities
team member HP/map/position
leave-team exact request
request-to-join exact request: 200051 / 9:targetRoleID
invite-target exact request: 200051 / 5:targetRoleID
MainThread queue/Update/Action.Invoke internals
```

If one of these fails in an implementation, investigate runtime integration/state freshness/server rejection before broad reverse engineering it again.

---

# Runtime evidence recording format

When any proof is performed, preserve:

```text
Date/client snapshot
PID/RoleID if relevant
Feature
Pre-state
Exact action / IDs / payload
Observed event/state sequence
Final state
PASS / FAIL / PARTIAL
What it proves
What it does NOT prove
```

Then update the canonical feature document and `AUTO_FEATURE_READINESS.md`; do not leave the result only in chat/logs.
