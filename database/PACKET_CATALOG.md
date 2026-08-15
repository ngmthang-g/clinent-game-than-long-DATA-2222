# TCP packet catalog

Source: decrypted `Interface.unity3d` → `TCPPacketDefine` Lua TextAsset. **169 exact symbolic constants** were parsed.

Full machine-readable list: `database/PACKET_IDS.csv`.

## High-value IDs

| Symbol | ID | Known role |
|---|---:|---|
| `CMD_ITEM_ACTION` | `100005` | item actions such as Equip/Use/Abandon/Split |
| `CMD_BAG_SORT` | `100006` | sort a bag/site |
| `CMD_SHOW_GAMEDIALOG` | `100007` | submit a dynamic GameDialog selection and also receive/open GameDialog |
| `CMD_CLIENT_STALL` | `100010` | player stall actions |
| `CMD_NPC_SHOP_DATA` | `200034` | server → client shop data; handler opens/refreshes NPCShop |
| `CMD_NPC_SHOP_BUY_REQUEST` | `200035` | buy/buy-back request |
| `CMD_NPC_SHOP_SELL_REQUEST` | `200036` | sell one item instance to current NPC shop |
| `CMD_REVIVE_DATA` | `200063` | revive/reincarnation request and revival UI data |
| `CMD_FUBEN_AUTO_DATA` | `200168` | dungeon auto state/data |
| `CMD_FUBEN_KILL_PROGRESS` | `200169` | dungeon kill progress |
| `CMD_FUBEN_QUERY_ALIVE` | `200170` | query surviving mobs/state in dungeon |
| `CMD_FUBEN_MATCHMAKING` | `200171` | dungeon matchmaking |
| `CMD_FUBEN_COMPLETE` | `200173` | dungeon completion |
| `CMD_FUBEN_SYNC_TARGET` | `200174` | dungeon target sync |

## Safety/semantics rule

Packet **name existence is not enough** to invent payloads. Payload is considered VERIFIED only where Lua source constructs it explicitly. This KB records exact payloads for revive, GameDialog, sell, bag sort and selected item actions in `analysis/11_EXACT_INTERNAL_ACTION_FLOWS.md`.