# Lua source catalog — semantic map

Source: decrypted `Interface.unity3d` TextAssets. The client embeds Lua source, not only prefabs.

Regex over recovered source identifies **339 script classes with colon-method definitions**. In addition, global infrastructure TextAssets include: `Global`, `Global_Constants`, `Global_Functions`, `Loader`, `Loader_Data`, `TCPCmdHandler`, `TCPCmdEventHandler`, `TCPPacketDefine`.

## High-value scripts

| Script | Why it matters |
|---|---|
| `AutoFight_Main` | full built-in train/PK/quest/fuben coordinator, target selection, movement, skill use, death/revive, NPC navigation |
| `AutoFight_FuBen` | scenario-driven dungeon engine |
| `AutoTrainMonster` | user settings for monster whitelist, scan range/lure/skills |
| `AutoHp` | HP/MP recovery, auto revive/comeback, Nga My heal/buff settings |
| `Utilities` | auto buff list and utility/reject/team settings |
| `Revival` | exact revive/reincarnation button packet actions |
| `NPCShop_SellItemTab` | exact sell/buy-back request payloads and sell filters |
| `RoleInfo_BagTab` | item Use/Equip/Abandon/Split and bag-sort packets |
| `BagItemsGrid` | item refresh/removal mapping and bag event handling |
| `GameDialog` | dynamic NPC/quest dialog selections; sends selected ID back to server |
| `TCPCmdHandler` | inbound packet → UI/service dispatch |
| `TCPPacketDefine` | 169 packet IDs |
| `Global_Constants` | item site/action, auto model, target type, revive type and other enum-like constants |

## Architectural conclusion

For future automation, **read Lua implementation before reverse-disassembling the same behavior from GameAssembly**. Lua often contains the exact payload and state logic in human-readable form. Native reverse should be targeted to methods/data not exposed by Lua.