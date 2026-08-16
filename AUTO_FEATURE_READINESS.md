# Auto Feature Readiness — what is already solved vs what still needs proof

Purpose: stop future AI from wasting time re-reversing automation features that are already understood.

Labels:

- **SOLVED CLIENT KNOWLEDGE** — enough semantic client knowledge exists to implement from the KB; normal coding/runtime integration remains.
- **PARTIAL / TARGETED PROOF** — broad architecture is solved; one narrow runtime/server behavior remains.
- **IMPLEMENTATION BRIDGE** — client internals are solved, but the external tool must still complete a live integration proof.
- **DESIGN ONLY** — orchestration policy is tool design rather than a discovered client contract.

Canonical external read-only schema: `analysis/35_RUNTIME_SNAPSHOT_CONTRACT.md`.

---

| Auto feature | Readiness | Already solved | Remaining narrow gap |
|---|---|---|---|
| Runtime local/map/bag/buff/cooldown scanner | **SOLVED CLIENT KNOWLEDGE** | semantic Game/RoleData queries + exact per-PID snapshot contract | external bridge must copy live values safely per PID |
| Nearby PeacePlayer scanner | **SOLVED CLIENT KNOWLEDGE** | RoleID/Name/Level/FactionID/HP/MaxHP/GuildName/AvartaID/TeamRank | Position/death only if a concrete non-team Buff path needs them |
| Nearby monster/Train target discovery | **SOLVED CLIENT KNOWLEDGE** | built-in `GetNearbySpritesWithPredicate`, `Type/IsDeath/RoleID/ResID/Position`, radius/whitelist concepts | none for basic Train implementation |
| Train start/stop | **SOLVED CLIENT KNOWLEDGE** | `C_AutoModel.Train=1`; `StartAutoFight(Train/None)` | none |
| Target/chase/combat skill path | **SOLVED CLIENT KNOWLEDGE** | SelectTarget/ChaseTarget/HasPath/RequestUsingSkill* / cooldown/progress guards | runtime integration only |
| Nga My skill identity | **SOLVED CLIENT KNOWLEDGE** | 406/407/408/423/424 exact identities; 407 Lua naming bug documented | none |
| Auto Buff candidate selection | **SOLVED CLIENT KNOWLEDGE** | nearby PeacePlayer fields + HP/MaxHP priority/filter model | none for read-only policy |
| Auto Buff cast on non-team PeacePlayer | **PARTIAL / TARGETED PROOF** | target/cast/range/cooldown donor path is known | prove server acceptance per intended beneficial skill/relationship |
| Local/team Nga My support donor | **SOLVED CLIENT KNOWLEDGE** | built-in team scan, range/chase, cast flow, dead teammate handling | none for understanding donor behavior |
| Bag full detection | **SOLVED CLIENT KNOWLEDGE** | `GetFreeBagSpace`, Bag site 10 | none |
| Item identity/classification | **SOLVED CLIENT KNOWLEDGE** | instance ID vs ItemID vs slot/site; runtime type/sell guards; Weapon rule; compact sell-policy contract | targeted static row materialization only if richer user policy needs it |
| Auto Sell request | **SOLVED CLIENT KNOWLEDGE** | packet 200036 + exact `instanceID:NpcShopID:ShopID` payload | none; do not trace again |
| Auto Sell transaction loop | **SOLVED CLIENT KNOWLEDGE** | one current instance -> sell -> wait server update -> rescan | runtime integration only |
| Vendor routing | **SOLVED MECHANISM / PARTIAL SERVICE MAP** | NPC DB + `GetNPCPosition` + GoToNPC + shop-state proof | promote specific vendor NPC/service mappings only as needed |
| NPC treatment navigation | **SOLVED MECHANISM** | NPC 339 candidate, GetNPCPosition/GoToNPC/GameDialog mechanism | exact live treatment selection/confirmation for chosen healer |
| NPC treatment selection | **PARTIAL / TARGETED PROOF** | dynamic `Selections[selectionID]=visibleText`, packet 100007 | capture actual treatment text/selectionID/outcome once |
| Revive / Đầu thai action | **SOLVED CLIENT KNOWLEDGE** | packet 200063; types 1/2/3 | none; runtime proof only belongs to tool integration |
| Loot/item-pack pickup | **SOLVED CLIENT KNOWLEDGE** | nearby ItemPack + path/move/click/pickup semantic flow | richer loot policy only if needed |
| Team state / member HP / position | **SOLVED CLIENT KNOWLEDGE** | C_TeamData, member fields, nearby precise position | none for scanner/follow basics |
| Leave team | **SOLVED CLIENT KNOWLEDGE** | `CMD_TEAM_ACTION`, payload `4:selfRoleID` | none; do not trace again |
| Request to join target's team | **SOLVED CLIENT KNOWLEDGE** | `CMD_OTHER_ROLE_COMMAND=200051`; `TeamRequestJoin=9`; payload `9:targetRoleID` | server acceptance still requires normal TeamID/C_TeamData state proof |
| Invite target to team | **SOLVED CLIENT KNOWLEDGE** | `CMD_OTHER_ROLE_COMMAND=200051`; `TeamInviter=5`; payload `5:targetRoleID` | server acceptance state proof only |
| Follow teammate | **SOLVED CLIENT KNOWLEDGE** | `TurnOnFollowTarget`, nearby MoveTo, cross-map GoTo fallback | none for semantic mechanism |
| MainThread internal dispatcher | **SOLVED CLIENT KNOWLEDGE** | Execute -> ConcurrentQueue -> Update -> dequeue -> Action.Invoke | none about dispatcher internals |
| External managed Action -> MainThread | **IMPLEMENTATION BRIDGE** | Action ABI/producer donors/required IL2CPP APIs known | one harmless live construction/rooting/callback proof |
| Captcha handling | **SOLVED SAFETY CONTRACT** | explicit Captcha state and manual submit | automation must pause; no auto-solve/bypass |
| Adaptive spot switching | **DESIGN ONLY, CLIENT INPUTS SOLVED** | deaths, loot/bag/map/train state sources exist | tool policy/metrics tuning, not more broad reverse |
| Multi-client orchestration | **DESIGN ONLY, CLIENT INPUTS SOLVED** | per-PID semantic state/action model understood | implementation/isolation testing per PID |

---

## Do not re-reverse these solved facts

Future AI should **not** spend time rediscovering:

- `Train=1` and semantic `StartAutoFight(Train)`;
- nearby PeacePlayer HP/MaxHP/name/RoleID fields;
- runtime snapshot field boundaries already documented in `analysis/35...`;
- exact sell packet/payload;
- exact revive/Đầu thai packet/types;
- dynamic GameDialog selection mechanism;
- `Game.GetNPCPosition` route principle;
- 407 = Xung Hư Dưỡng Khí, 423 = actual Kim Châm Độ Kiếp;
- bag `ID` instance vs `ItemID` template distinction;
- team member HP/map/position schema;
- leave-team action `4:selfRoleID`;
- **request-to-join action `200051 / 9:targetRoleID`**;
- invite-target action `200051 / 5:targetRoleID`;
- MainThread queue/Update/Action.Invoke internals.

If implementation fails despite using these contracts, debug the **runtime bridge/state/proof** first rather than broad-reversing the client again.

---

## Highest-value remaining proofs for the actual auto tool

Only a few narrow proofs materially block advanced features:

1. external valid managed `System.Action` -> `MainThread.Execute` live callback;
2. non-team PeacePlayer acceptance for the exact Nga My support skill(s) the tool will use;
3. exact live `Trị liệu` dialog sequence/outcome at the chosen healer;
4. any missing actor field only when a concrete feature cannot be completed from current snapshots;
5. vendor-service promotion for the exact NPCs/maps actually used by Auto Sell, only where runtime shop/dialog state is still unknown.

**Join-party request construction is no longer a research gap.** The request is already source-verified as `CMD_OTHER_ROLE_COMMAND=200051`, payload `9:targetRoleID`; only normal server response/membership proof remains during implementation.

Everything else should first move from research into implementation, not into more broad reverse engineering.