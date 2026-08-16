# AI PROJECT KNOWLEDGE & ENGINEERING LINEAGE PROTOCOL — V2
## Optimized long-term memory standard for AI-assisted development

> **Goal:** Preserve both current CODE and the engineering lineage that explains why the code became this way.
>
> Required chain:
>
> `User Request → Previous State → Implementation → Build/CI → Runtime → Bug/Regression → Fix/Revert → Known-Good → Current Source`
>
> A future AI must be able to continue development without rediscovering known facts, repeating failed approaches, or casually breaking user-confirmed behavior.

# 1. CORE RULES

## 1.1 Knowledge is part of the product

```text
SOURCE CODE
= current implementation

PROJECT_KNOWLEDGE.md
= current snapshot + central knowledge index

CHANGELOG.md
= concise version chronology

docs/
= detailed history, features, bugs, decisions, evidence, reverse-engineering
```

A version is incomplete if source changed but knowledge was not updated.

## 1.2 Never erase engineering history

For every new version:
- append new history;
- update current summaries;
- preserve old requests, failures, regressions, reverts, runtime evidence and known-good references;
- preserve uncertainty instead of inventing continuity;
- never rewrite a failed experiment as if it never happened.

## 1.3 BUILD PASS is not RUNTIME PASS

Use explicit states:

```text
NOT BUILT
BUILD FAILED
BUILD PASS
CI FAILED
CI PASS
RUNTIME UNTESTED
RUNTIME PARTIAL PASS
RUNTIME PASS
RUNTIME FAIL
REGRESSION
REVERTED
KNOWN-GOOD
```

Rules:
- `BUILD PASS ≠ RUNTIME PASS`
- `CI PASS ≠ RUNTIME PASS`
- self-test PASS ≠ user-confirmed runtime
- only runtime evidence can establish `RUNTIME PASS`
- `KNOWN-GOOD` requires strong runtime evidence

## 1.4 Evidence labels

```text
CONFIRMED  = directly supported by evidence
LIKELY     = strong but incomplete evidence
UNKNOWN    = insufficient evidence
DISPROVEN  = evidence contradicts assumption
DEPRECATED = formerly accepted, no longer current
FAILED     = attempted and failed
```

Never promote `LIKELY`/`UNKNOWN` without new evidence.

## 1.5 Evidence priority

When evidence conflicts:
1. reproducible runtime logs/tests;
2. current source for current implementation;
3. user runtime observation;
4. CI/build artifacts for build state;
5. git history/diffs/releases for historical state;
6. project knowledge documents;
7. AI inference.

Source proves implementation, not runtime success. Runtime observation proves behavior, not necessarily root cause.

# 2. KNOWLEDGE STRUCTURE

Recommended:

```text
PROJECT/
├── PROJECT_KNOWLEDGE.md
├── CHANGELOG.md
├── README.md
├── docs/
│   ├── history/
│   │   └── VERSION_vX.Y.Z.md
│   ├── features/
│   │   └── <FEATURE>.md
│   ├── bugs/
│   │   └── BUG_REGISTRY.md
│   ├── decisions/
│   │   └── DECISIONS.md
│   ├── evidence/
│   │   └── EVIDENCE_REGISTRY.md
│   ├── investigations/
│   └── reverse-engineering/
└── src/
```


# 3. FILE RESPONSIBILITIES

## PROJECT_KNOWLEDGE.md

Must contain:
- project identity/current version;
- architecture and hard rules;
- runtime-confirmed working behavior;
- built-but-untested behavior;
- regressions/open bugs;
- known-good summary;
- failed/unsafe mechanism summary;
- important technical facts;
- links to deeper docs.

## CHANGELOG.md

Concise history of all meaningful versions:
- requested;
- added/changed/fixed/reverted;
- build/CI;
- runtime;
- regression;
- known-good;
- next-version note.

## docs/history/

One detailed file per meaningful version.

Example:
```text
docs/history/VERSION_v1.4.1.md
```

## docs/features/

One file per important subsystem.

Examples:
```text
AUTO_TRAIN.md
AUTO_FIGHT.md
CROSS_MAP_CONFIRM.md
AUTO_SELL.md
CLICK_ENGINE.md
```

## Registries

```text
docs/bugs/BUG_REGISTRY.md
docs/decisions/DECISIONS.md
docs/evidence/EVIDENCE_REGISTRY.md
```

## docs/reverse-engineering/

Store expensive-to-rediscover facts:
- class/method/API;
- IL2CPP metadata;
- IDs/ResIDs;
- offsets/RVAs/signatures;
- protocols;
- file formats;
- object layouts;
- call chains;
- thread requirements;
- build-specific constraints.

# 4. STABLE IDS

## REQ-xxx
Meaningful user requirement.

```text
REQ-xxx
Requested in:
User intent:
Acceptance behavior:
Status: OPEN / IMPLEMENTED / PARTIAL / REVERTED / DEPRECATED
Implemented in:
Runtime evidence:
Related BUG / feature:
```

## BUG-xxx
Stable bug/regression ID. Never reuse.

## DEC-xxx
Stable architectural/design decision ID.

## EVID-xxx
Stable important evidence ID.

# 5. AI STARTUP PROCEDURE

Before modifying code, read:
1. this protocol;
2. `PROJECT_KNOWLEDGE.md`;
3. linked docs for affected feature/version/bug/decision;
4. `CHANGELOG.md`;
5. README;
6. relevant source/tests;
7. git/PR/issue history when needed.

Then identify:

```text
Current Version
Affected Feature
Current Source State
Last Known-Good
Open Bugs / Regressions
ACTIVE Decisions
Known Failed Approaches
User-Confirmed Runtime Behavior
Unverified Assumptions
Relevant REQ IDs
```

# 6. PRE-CODE CHECKLIST

```text
[ ] What feature is affected?
[ ] Which version introduced it?
[ ] What is last known-good?
[ ] Is current behavior runtime-confirmed?
[ ] Is there a BUG/regression history?
[ ] Was this solution already tried?
[ ] Is there an ACTIVE decision?
[ ] Am I changing historically significant timing/API/state?
[ ] Can I diagnose before redesigning?
[ ] What evidence supports the theory?
```

# 7. PROJECT_KNOWLEDGE.md TEMPLATE

```md
# PROJECT KNOWLEDGE

## Project Identity
- Name:
- Repository:
- Primary branch:
- Development branch:
- Current version:
- Last known-good release:
- Platform / framework / build system:

## Project Goal

## Current State
### Runtime-confirmed working
### Built but runtime-untested
### Partial / unstable
### Known regressions
### Open bugs
### Current priorities

## Architecture
## Major Components
## Hard Architectural Rules
## Known-Good Summary
## Failed / Unsafe Mechanisms
## Important Technical Facts
## Important IDs / APIs / Data Sources
## Persistence / Configuration
## Build Environment
## Open Questions

## Knowledge Index
### Requirements
### Bugs
### Decisions
### Evidence
### Feature History
### Version History
### Reverse-Engineering Docs
```

Do not duplicate complete version histories here.

# 8. VERSION LINEAGE — MANDATORY

Every meaningful version records:

```text
Version:
Based On:
Reason Created:
Previous Runtime State:
Last Known-Good:
Regression From:
Supersedes:
Superseded By:
Related REQ:
Related BUG:
Related Features:
```

# 9. VERSION HISTORY FILE

File:
```text
docs/history/VERSION_vX.Y.Z.md
```

Required sections:

## A. Identity / Lineage
```text
Version:
Date:
Based On:
Reason Created:
Last Known-Good:
Regression From:
Supersedes:
Superseded By:
```

## B. User Requests
Preserve real engineering intent. Use REQ IDs when useful.

## C. State Before Modification
Record:
- working behavior;
- broken behavior;
- user runtime complaints;
- limitations;
- inherited bugs;
- previous known-good behavior.

## D. Investigation / Root Cause
Record source, versions, logs, files/binaries and hypotheses inspected.

```text
Root Cause:
CONFIRMED / LIKELY / UNKNOWN / DISPROVEN

Evidence:
EVID-xxx / description
```

## E. Changes Made

For each important change:

```text
File / Module:
Function / Class:
Previous Behavior:
Problem:
New Behavior:
Implementation:
Reason:
Data Source:
```

## F. Important Implementation Details
Record only details future AI would otherwise need to rediscover:
- state transitions;
- APIs;
- constants/timing;
- retries;
- protocols;
- IDs/offsets;
- config locations;
- persistence formats;
- thread constraints.

## G. Files / Components Changed
```text
Modified:
Added:
Removed:
```

## H. Build / CI History
Preserve failures and final result.

```text
Initial Build:
Cause:
Correction:
Final Build:
CI:
Run:
Commit:
Artifact:
```

## I. Runtime Result
```text
RUNTIME: UNTESTED / PARTIAL PASS / PASS / FAIL
Confirmed Working:
Still Failing:
Awaiting Test:
```

## J. Regression / Revert / Failed Attempts

When applicable:

```text
Feature:
Last Known-Good:
First Confirmed-Bad:
Versions Between:
What Stayed The Same:
What Changed:
Root Cause Status:
Approach Attempted:
Result:
Why Abandoned/Reverted:
Can Retry:
Evidence:
```

## K. Known-Good Established
Only if runtime-confirmed:

```text
Subsystem:
Version:
Behavior:
Runtime Evidence:
Critical Timing / Constants:
Do-Not-Change Warning:
```

## L. Remaining Bugs / New Knowledge / Decisions
Link BUG/DEC/EVID entries.

## M. Handoff
Record:
- unresolved work;
- what to inspect first;
- what not to change first;
- next evidence/log needed.

# 10. FEATURE HISTORY FILE

File:
```text
docs/features/<FEATURE>.md
```

Template:

```md
# FEATURE: <NAME>

## Purpose
## Current Implementation
## Current Runtime Status
## Current Known-Good
## Related REQ / BUG / DEC

## Version Timeline
### vX
- request:
- implementation:
- build:
- runtime:
- result:

### vY
- inherited problem:
- change:
- regression/fix:
- runtime:

## Failed / Reverted Approaches
## Important APIs / Timing / Constants
## Do-Not-Break Rules
## Open Questions
## Next Diagnostic Step
```

# 11. KNOWN-GOOD RULE

Only runtime evidence establishes `KNOWN-GOOD`.

Record:

```text
Subsystem:
Known-Good Version:
Behavior:
Runtime Evidence:
Relevant File/Function:
Critical Timing/Constants:
Reason Protected:
Do-Not-Change Warning:
```

# 12. BUG REGISTRY

File:
```text
docs/bugs/BUG_REGISTRY.md
```

Template:

```text
## BUG-xxx — Title

Status:
OPEN / PARTIAL / FIXED-BUILD / FIXED-RUNTIME / REGRESSION / DEPRECATED

Severity:
First Observed:
Last Tested:
Last Known-Good:
First Confirmed-Bad:
Related Feature / REQ:
Known Evidence:
Unknowns:
Root Cause:
Attempts:
Current Workaround:
Fixed In:
Runtime Verified In:
Next Diagnostic Step:
Do-Not-Do:
```

# 13. DECISION REGISTRY

File:
```text
docs/decisions/DECISIONS.md
```

```text
## DEC-xxx

Date / Version:
Status: ACTIVE / SUPERSEDED / DEPRECATED
Decision:
Context:
Alternatives:
Why Rejected:
Evidence:
Reason:
Consequences:
Affected Features:
Superseded By:
```

# 14. EVIDENCE REGISTRY

File:
```text
docs/evidence/EVIDENCE_REGISTRY.md
```

```text
## EVID-xxx

Type:
USER_RUNTIME / LOG / CI / SOURCE / DIFF / BINARY / FILE_ANALYSIS /
VIDEO / SCREENSHOT / REVERSE_ENGINEERING

Date / Version:
Source:
Observation:
Supports:
Does NOT Prove:
Confidence:
Limitations:
```

# 15. FAILED APPROACH / CORRECTION RULES

For important failed approaches record:

```text
Approach:
Version:
Goal:
Reason Attempted:
Result:
Failure Mode:
Evidence:
Reverted In:
Lesson:
Can Retry:
Retry Conditions:
```

For incorrect old knowledge:

```text
CORRECTION-xxx
Old Knowledge:
New Finding:
Evidence:
Affected Versions:
Impact:
Old Status: DEPRECATED / DISPROVEN
```

# 16. CHANGELOG TEMPLATE

```md
## [vX.Y.Z] - YYYY-MM-DD

### Requested
- REQ-xxx: ...

### Added / Changed / Fixed
- ...

### Removed / Reverted
- ...

### Files / Modules
- ...

### Build
- Initial:
- Final:
- CI:
- Commit:
- Artifact:

### Runtime
- Status:
- Confirmed working:
- Still failing:
- Awaiting test:

### Regression / Known-Good / Related Bugs
- ...

### Next Version Notes
- ...
```

# 17. USER RUNTIME REPORT RULE

When the user reports runtime results, update knowledge immediately, even without a new code version.

Update:
1. affected feature docs;
2. tested version history;
3. BUG_REGISTRY;
4. CHANGELOG runtime section;
5. EVIDENCE_REGISTRY when valuable.

Example:

```text
User:
AutoFight works.
Sell works.
Confirm still fails.

Knowledge:
AutoFight = RUNTIME PASS
AutoSell = RUNTIME PASS
Cross-map Confirm = RUNTIME FAIL
```

# 18. REGRESSION AND REVERT RULE

If previously working behavior breaks, explicitly record:

```text
Feature:
Last Known-Good:
First Confirmed-Bad:
Versions Between:
What Was Compared:
What Stayed The Same:
What Changed:
Root Cause:
Current Workaround:
Evidence:
```

If reverting:

```text
Reverted Subsystem:
Reference Version:
Why Selected:
Runtime Evidence for Reference:
Behavior Restored:
Newer Behavior Removed:
Related BUG:
What Must Be Retested:
```

# 19. PROTECT STRANGE BUT PROVEN CODE

Before “cleaning” odd code, inspect history.

Examples:
- unusual delay;
- extra stall wait;
- duplicate-looking state;
- two-step click;
- fallback loop;
- migration workaround.

If historically significant:

```text
Reason:
Known-Good Version:
Evidence:
Rule:
Do not optimize without comparative runtime evidence.
```

# 20. REVERSE-ENGINEERING RULE

If information was expensive to discover, save it:
- classes/methods/APIs;
- metadata;
- offsets/RVAs/signatures;
- IDs/ResIDs;
- packets;
- object layouts;
- call chains;
- thread requirements;
- file formats;
- crypto/packing;
- server/client responsibility.

For build-specific data:

```text
Value:
Confirmed Build:
Stable Resolution:
Warning:
Do not treat build-specific value as universal.
```

# 21. NOISE CONTROL

Do not make knowledge a chat log.

Preserve:

```text
Request → Analysis → Evidence → Implementation → Build → Runtime → Result → Knowledge
```

Keep:
- important numbers/timing;
- IDs/APIs;
- state transitions;
- errors/root causes;
- failed solutions;
- test conditions;
- architectural consequences.

Usually omit:
- trivial renames;
- formatting-only edits;
- temporary logs with no future value;
- repetitive compiler output.

# 22. COMPLETE HISTORY, SELECTIVE RETRIEVAL

As data grows:

```text
PROJECT_KNOWLEDGE.md → current snapshot/index
docs/history/        → per-version detail
docs/features/       → feature lineage
docs/bugs/           → bug history
docs/decisions/      → decisions
docs/evidence/       → proof
docs/reverse-engineering/ → deep findings
```

# 23. MASTER HISTORY RECONSTRUCTION

When adopting this protocol in a mature project, reconstruct from available:
- commits/tags/branches;
- PRs/releases;
- old source/builds;
- CI/logs;
- existing docs;
- user reports;
- project conversations.

For each recoverable version:

```text
Version:
Approximate Date:
Based On:
Reason Created:
User Request:
Changes:
Build / CI:
Runtime:
Known Issues:
Known-Good:
Regression:
Reason for Next Version:
Evidence:
Confidence:
```

If unavailable:

```text
UNKNOWN — not recoverable from available evidence.
```

# 24. MINIMUM INFORMATION PER VERSION

Every meaningful version must answer:

```text
1. Why did it exist?
2. What did the user ask for?
3. What version was it based on?
4. What was wrong before?
5. What changed and where?
6. Did build/CI pass?
7. Did real runtime pass?
8. What worked?
9. What failed?
10. Was there a regression?
11. What was last known-good?
12. What became known-good?
13. What was reverted/abandoned?
14. What bugs remain?
15. What should the next AI inspect first?
```

Use `UNKNOWN` when necessary.

# 25. VERSION COMPLETION CHECKLIST

```text
[ ] Requirements recorded / REQ IDs updated
[ ] Source changes recorded
[ ] Build/CI results recorded
[ ] Meaningful failed build preserved
[ ] Runtime status explicit
[ ] Version history updated
[ ] Feature history updated
[ ] BUG registry updated
[ ] Known-good updated if applicable
[ ] Failed/reverted approach preserved
[ ] DEC/EVID updated if applicable
[ ] PROJECT_KNOWLEDGE snapshot/index updated
[ ] CHANGELOG updated
[ ] Remaining bugs + handoff recorded
[ ] Release/source contains current knowledge/docs
```

# 26. EXPERIMENTAL FIX RULE

If speculative:

```text
Implementation: EXPERIMENTAL
Root Cause: LIKELY / UNKNOWN
BUILD: PASS / FAIL
CI: PASS / FAIL
RUNTIME: UNTESTED
```

# 27. USER-CONFIRMED KNOWN-GOOD

When the user reports reliable success:
1. create/update EVID;
2. mark runtime PASS;
3. update feature history;
4. update known-good;
5. preserve critical timing/constants;
6. protect behavior from casual redesign.

# 28. HANDOFF FOR A NEW AI

A new AI must:
1. read this protocol;
2. read `PROJECT_KNOWLEDGE.md`;
3. follow links for affected feature/bug/version/decision;
4. read `CHANGELOG.md`;
5. inspect current source;
6. confirm branch/version;
7. check last known-good, bugs, failed attempts, decisions and runtime evidence;
8. only then modify code.

# 29. FINAL PRINCIPLE

Project memory must preserve:

```text
REQ
→ Version
→ Previous State
→ Implementation
→ Build / CI
→ Runtime Evidence
→ BUG / Regression
→ Fix / Revert
→ KNOWN-GOOD
→ DECISION
→ Current Source
```

A future AI must be able to answer:
- what the user requested in any important version;
- why that version existed;
- what changed and where;
- what failed before;
- whether build/CI passed;
- whether runtime was actually confirmed;
- which version is last known-good;
- which regression caused later work;
- which attempted fix failed;
- why odd timing/state/API behavior exists;
- what must not be changed casually;
- where deeper evidence lives.

If evidence is missing:
```text
UNKNOWN
```

If build passes but runtime is not tested:
```text
RUNTIME UNTESTED
```

If older behavior is user-confirmed:
```text
KNOWN-GOOD
```

> **Never silently erase engineering history.**
>
> **Keep history complete, but make retrieval selective.**
>
> **Every version inherits both CODE and KNOWLEDGE from previous versions.**

# 30. INITIALIZATION

When first introducing this protocol:
1. inspect current source/version;
2. create/repair `PROJECT_KNOWLEDGE.md` and `CHANGELOG.md`;
3. create the `docs/` knowledge structure;
4. reconstruct MASTER HISTORY from available evidence;
5. create meaningful per-version and critical feature history files;
6. create BUG/DECISION/EVIDENCE registries;
7. identify last known-good runtime references;
8. preserve failed/reverted approaches;
9. mark unrecoverable facts `UNKNOWN`;
10. update the current-state index;
11. maintain this protocol continuously.

This protocol remains active until the user explicitly changes or replaces it.

# END OF PROTOCOL V2
