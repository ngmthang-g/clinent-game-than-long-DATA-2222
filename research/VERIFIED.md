# Verified Findings

This file contains only findings that have been confirmed by direct evidence or repeatable testing for a specific client build.

## Entry format

Use this template for every verified finding:

```markdown
## <Finding title>

Status: VERIFIED
Client build: <version/build>
Client hashes: <relevant SHA-256 values>

### Summary
<What is confirmed>

### Evidence
- <binary/runtime evidence>
- <repeatable test result>

### Technical details
- Namespace:
- Class:
- Method:
- Field:
- Module:
- Relevant signature/identifier:

### Runtime constraints
- Thread requirement:
- Required state:
- Known side effects:

### Related documents
- <paths>

### Last verified
<date>
```

## Verification rules

A finding belongs here only when at least one strong verification route exists, such as:

- repeatable runtime observation;
- confirmed metadata/class/method mapping tied to the current client;
- direct binary evidence with a reproducible derivation;
- action sequence tested successfully multiple times;
- data field validated against independently observable in-game state.

Do not put guesses, inferred semantics, untested offsets, or one-off coincidences in this file.

## Current verified findings

None recorded in this knowledge-base version yet.

Existing discoveries from earlier experiments should be migrated here only after their evidence and client-build identity are documented.
