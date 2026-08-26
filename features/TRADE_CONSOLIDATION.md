# DỒN ĐỒ / TRADE — canonical tool feature route

Read `analysis/40_TRADE_CONSOLIDATION_RUNTIME_STACK.md`.

Trade capacity is exactly 9 item slots per side. Batching must use fresh unbound live instances, current ExchangeID, ItemsTrade/Lock/Done state, final session close and fresh bag snapshots. The number 9 is a capacity limit, not proof that a round succeeded.
