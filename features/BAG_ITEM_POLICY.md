# TAY NẢI / ITEM POLICY — canonical tool feature route

Read `analysis/41_BAG_ITEM_USE_DROP_POLICY_STACK.md`, `database/AUTO_SELL_CLASSIFICATION.md`, and compact item/equipment data only as needed.

Manual Use/Abandon/Destroy/Move/Split are verified semantic actions. AutoUsingItem and AutoDrop are not verified executors in the shipped Lua; AutoDrop also has a persisted-field load bug. Destructive actions require explicit tool policy + fresh live instance guard.
