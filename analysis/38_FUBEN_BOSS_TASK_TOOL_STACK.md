# 38 — FuBen / Boss / Task automation stack

Status: **VERIFIED from decrypted `Config.unity3d` + shipped `AutoFight_FuBen.lua`, `AutoFuBen.lua`, `AutoFight_Main.lua`, `Loader.lua`, TCP handlers/constants.** Derived boss labels are explicitly separated from exact template `Type=Boss` evidence.

## 1. Static FuBen database

`FuBenScenarios.xml` contains **19 scenarios**. Every scenario carries:

`ID, Name, DungeonMapID, Timeout, MinPlayers, MinLevel, GatherMapID, GatherNPCID, GatherX, GatherY, RequestActiveCardMonth`.

The 19 scenarios expand to **114 steps** and **268 executable actions** in the normalized tool database. Action totals:

- GoTo 72
- Kill 72
- Wait 31
- GoToNPC 19
- SelectDialog 19
- WaitMapChange 19
- Notify 19
- InteractNPC 14
- UsePortal 3

Canonical machine-readable files:

- `database/fuben/FUBEN_SCENARIOS.csv`
- `database/fuben/FUBEN_ENTRY_NPCS.csv`
- `database/fuben/FUBEN_ACTIONS.csv`
- `database/fuben/FUBEN_KILL_TARGETS.csv`

## 2. NPC versus Boss taxonomy

Do not conflate NPC and combat boss.

- `NPCs.xml`: service/quest/entry identities (`ID, Name, ResName, Avarta`).
- `Monsters.xml`: combat templates including `Type=Boss`.
- frozen snapshot: **3,579 Boss monster templates**, grouped into **578 distinct display names** in `database/static/monsters/BOSS_NAME_INDEX.csv`.

FuBen entry/service actors are NPCs; combat bosses are monster templates. A route can use an NPC to enter/select a dungeon and then target Boss monsters inside it.

## 3. FuBen Kill target semantics

There are **72 Kill actions**. Each Kill step may use a direct `MonsterID` or level-banded `Templates` (`MonsterID, MinLevel, MaxLevel`). Therefore the correct resolver is:

`Scenario + Step + current level band -> configured MonsterID/ResID -> runtime spawned actor`.

Do not hardcode one global boss ID merely from a visible name.

In the frozen data:

- 42/72 Kill actions have configured monster templates whose mapped `Monsters.Type` are all exactly `Boss`;
- 39/72 Step IDs/names syntactically signal boss;
- these are different evidence classes and are both preserved in `FUBEN_KILL_TARGETS.csv`.

`KillCount=1` alone is **not** boss proof.

## 4. Exact FuBen packets

Verified packet IDs:

- `200168 CMD_FUBEN_AUTO_DATA`
- `200169 CMD_FUBEN_KILL_PROGRESS`
- `200170 CMD_FUBEN_QUERY_ALIVE`
- `200171 CMD_FUBEN_MATCHMAKING`
- `200172 CMD_FUBEN_MATCHMAKING_NOTIFY`
- `200173 CMD_FUBEN_COMPLETE`
- `200174 CMD_FUBEN_SYNC_TARGET`

Observed request forms:

- query all alive: `QUERY`
- query configured ResIDs: `resIDCSV:maxCount`
- sync target: CSV ResIDs, or empty payload when clearing
- matchmaking register: `0:scenarioID:desiredMembers:minInviteLevel`
- cancel: `1:scenarioID`
- accept invite: `2:leaderRoleID`
- decline invite: `3:leaderRoleID`
- action values 4 and 5 are also emitted by shipped Lua around finish/matchmaking lifecycle; preserve them as observed until the exact server-side semantic is proven from a request path/result state.

## 5. FuBen settings actually consumed

Verified settings include:

`SelectedFuBen, AutoRepeat, RepeatCount, FollowLeader, AcceptFuBenInvite, AutoInviteMembers, AutoRevive, DesiredMembers, MinInviteLevel, ScheduleEnabled` plus 8 schedule slots (`Enabled,Hour,Minute,FuBen`).

UI ranges observed:

- RepeatCount: 1..10
- DesiredMembers: 1..6
- MinInviteLevel: 10..150 in steps of 10.

`AutoRepeat/RepeatCount` are not decorative: `AutoFight_FuBen` consumes them at completion and restarts when allowed.

Leader gathering uses `max(scenario.MinPlayers, DesiredMembers)` capped at 6 and checks team readiness/proximity before entry. Follower flow follows leader and participates in combat.

## 6. FuBen runtime combat donor

Inside a dungeon, the shipped engine composes semantic runtime actions:

`GetNearbySpritesWithPredicate -> Type/ResID/RoleID/Position -> ReloadTarget -> HasPath -> SelectTarget -> ChaseTarget -> RequestUsingSkillWithTarget/Pos`.

It also has HP-not-decreasing/ignore-target handling and server alive/progress synchronization. Tool FuBen automation should reuse the same state/action/proof discipline as Auto Train, not a blind coordinate macro.

## 7. Task database

`Tasks.xml` contains **516 tasks**. Frozen task-type distribution:

- Delivery (0): 221
- KillMonster (1): 206
- LootItemFromMonster (2): 71
- EnterArea (4): 7
- TransferNPC (5): 6
- LevelUp (6): 3
- JoinFaction (8): 1
- CallFightPet (9): 1

The enum supports more task types, but the frozen static table has no rows for CollectItem(3), CapturePet(7), UseItem(10), CraftItem(11). Do not claim frozen content for absent types merely because the enum exists.

TaskRule distribution: rule0=223, rule1=173, rule2=120.

Machine-readable task data:

- `database/static/tasks/TASK_INDEX.csv`
- `database/static/tasks/TASK_OBJECTIVES.csv`

The objective file preserves nested objective attributes instead of flattening away unknown/type-specific fields.

## 8. Runtime authority

Static FuBen/Task rows answer configured identity/route/objective. Runtime/server state remains authoritative for:

- current dungeon instance/map readiness;
- current spawned target/death/position;
- current task progress Parameters;
- current GameDialog selection IDs;
- current team membership/proximity;
- completion/reward/entry acceptance.

Recommended contract:

`static scenario/task -> current runtime snapshot -> one semantic action -> server/runtime proof -> fresh snapshot`.
