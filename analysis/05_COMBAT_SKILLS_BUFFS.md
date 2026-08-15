# Combat / Skills / Buffs / Auto Fight

## 1. Kết luận kiến trúc

Metadata/string evidence cho thấy combat không phải một black box. Client có API cấp cao để query/use skill, select/chase target, inspect buff và xử lý nhiều magic effect semantics. Đây là nền tảng tốt cho auto combat/buff dựa trên state thật thay vì click/macro.

## 2. Skill/ability API đã thấy

Trong `LuaSystemAPI_Game` có các symbol:

- `GetAbilities`
- `GetAbilityLevel`
- `GetAbilityTemplateData`
- `GetAbilityName`
- `GetAbilityDescription`
- `GetAbilityIcon`
- `GetAbilityLevelUpExp`
- recipe-related getters
- `UseSkill(skillID)`
- `RequestUsingSkill`
- `RequestUsingSkillWithPos`
- `RequestUsingSkillWithTarget`
- `GetSkillLuaData`
- `IsSkillRequireTarget`
- `CanUseSkill`

### Diễn giải

Có ít nhất hai tầng:

- API semantic để UI/Lua yêu cầu dùng skill;
- network/event processing để server xác nhận damage/heal/buff/state.

Tool nên ưu tiên action/game API hợp lệ thay vì thao tác phím nếu mục tiêu là ổn định.

## 3. Target/chase state

Các API liên quan:

- `SelectTarget`
- `ClickToObject`
- `ChaseTarget`
- `get_CurrentChaseTargetID`
- `IsSelectTargetDie`
- `IsAllowDeadTarget`
- `BugTarget`
- `GetDistance`
- `HasPath`
- `CanMove`

Từ đó có thể xây target policy:

```text
query nearby enemies
 -> filter alive / valid / reachable
 -> score by distance/type/HP
 -> SelectTarget
 -> chase/request skill
 -> observe death/target change
```

Không cần nhận diện quái bằng ảnh nếu nearby object data đã được map.

## 4. Buff API

Đã thấy:

- `GetBuffs`
- `GetBuffProperties`
- `HasBuff`
- `GetBuffData`
- `GetTargetBuffIcons`
- `SendRemoveBuff(buffID)`

Điều này tạo cơ sở cho auto buff chính xác hơn logic “HP thấp thì buff”. Khi exact return type được map, có khả năng đọc:

- buff ID/template;
- owner/target;
- stack;
- duration/remaining time;
- properties/category;
- positive/negative flags.

Danh sách field exact chưa được VERIFIED, nhưng API names chứng minh subsystem tồn tại.

## 5. Magic/effect semantics thấy trong metadata

String heap có số lượng lớn `magic_*` flags/keys. Các ví dụ đáng chú ý:

- `magic_reduce_skill_cd` và nhiều biến thể;
- `magic_total_targets`;
- `magic_max_stacks`;
- `magic_state_no_clear_on_death`;
- `magic_remove_buff_on_max_stack`;
- `magic_buff_realtime_db`;
- `magic_double_strikes` / `magic_triple_strikes`;
- `magic_buff_group`;
- `magic_buff_no_save_db`;
- `magic_remove_buff_on_timeout`;
- `magic_special_res_id`;
- `magic_mark_hp_from_owner_p`;
- `magic_buff_remove_on_move`;
- `magic_buff_remove_on_action`;
- `magic_can_positive_remove`;
- `magic_fall_from_mount`;
- `magic_force_monster_attack_self`;
- `magic_revive_on_death`;
- `magic_ignore_target_defense`;
- `magic_ignore_target_res`;
- `magic_drag_target`;
- `magic_doubledamage_next_attack`;
- `magic_unable_to_use_skill`;
- `magic_blink_to_target`;
- `magic_blink_to_position`;
- `magic_reset_all_skill_cd`;
- `magic_revive_death`;
- `magic_reduce_skill_cast_time`;
- `magic_chaining_no_interupt`;
- `magic_reduce_chaining_time`;
- `magic_skill_always_hit`;
- `magic_skill_always_crit`;
- `magic_invisibility`;
- `magic_swap_position`;
- `magic_see_hidden_trap`;
- `magic_activate_trap`;
- `magic_summon_puppet`;
- `magic_callback_puppet`;
- `magic_swap_puppet_position`;
- `magic_see_invisibility_low/high`;
- `magic_negate_dead`;
- `magic_skill_start_event`;
- `magic_skill_collide_event`;
- `magic_skill_vanish_event`;
- `magic_autoskill`;
- `magic_call_skill_random...`.

### Ý nghĩa

Config skill/buff có vẻ giàu data hơn chỉ damage number. Nếu extract đúng config, có thể xây offline skill database để hiểu:

- buff/debuff semantics;
- target requirements;
- cooldown modifiers;
- death/revive behavior;
- mobility/blink/drag;
- invisibility/trap;
- chain/auto-skill behavior.

Đây là PROBABLE cho schema chi tiết cho tới khi bảng asset cụ thể được decode.

## 6. Network commands liên quan combat

Các command names đã thấy gồm:

- `CMD_USE_SKILL`
- `CMD_NEW_MISSILE`
- `CMD_NEW_SKILL_EXPLODE`
- `CMD_SKILL_DAMAGE`
- `CMD_SKILL_HEAL`
- `CMD_OBJECT_DEATH`
- `CMD_REVIVE`
- `CMD_ADD_BUFF`
- `CMD_UPDATE_BUFF`
- `CMD_REMOVE_BUFF`
- `CMD_MOVESPEED_CHANGED`
- `CMD_DRAG_TARGET`
- `CMD_DO_ACTION`
- `CMD_DO_LEAP`
- `CMD_ACTIVATE_TRAP`
- `CMD_PUPPET_ATTACK`
- `CMD_UPDATE_MONSTER_TYPE`
- `CMD_PK_VALUE`.

Không nên suy ra packet direction chỉ từ tên; hãy map caller/processor khi cần exact behavior.

## 7. Auto Fight evidence

String evidence có `DrawCicleAutoFight` (typo đúng như binary) và `RemoveAutoFightMark` trong scene-related cluster. Cùng với `get/set_EnableAutoF1`, `RangerAuto`, `AutoSetFlag`, điều này gợi ý mạnh rằng game có **built-in auto-fight state/radius/marker**, không chỉ một UI button giả.

### PROBABLE architecture

```text
Auto UI selection
 -> set auto mode/flag/range config
 -> scene draws auto-fight circle/mark
 -> internal target/skill loop operates
```

Exact method làm “chọn chế độ Đánh quái” chưa được xác nhận. Future AI nên trace UI/Lua action khi người dùng tự bật đúng mode, thay vì tìm coordinate nút.

## 8. Auto buff theo HP/MaxHP

Nếu nearby player/entity data + buff API được resolve, policy có thể là:

```text
candidates = nearby eligible players
sort by MaxHP descending (hoặc policy khác)
for each:
    if HP% below threshold AND missing desired buff:
        select/target
        cast buff skill
        wait buff/event/skill completion
        rescan
```

Điểm quan trọng: **HP priority và buff presence là hai signal khác nhau**. Nếu chỉ nhìn HP sẽ spam buff lên người đã có buff hoặc bỏ qua duration/stack.

## 9. Combat recorder khả thi

Với event commands/processors, có khả năng xây observer cho:

- skill used;
- damage/heal;
- crit nếu protocol/data có flag;
- target death;
- XP/loot events nếu map được;
- kill rate, death/hour, loot/hour.

Đây là hướng analytics; không phải tất cả field đã được map.

## 10. Main-thread/state requirement

`UseSkill`/UI/target action có thể chạm Unity/Lua/game state. Không gọi từ arbitrary worker thread. Pattern:

```text
read-only observer
 -> decide
 -> enqueue one action
 -> Unity/main-thread dispatch
 -> wait concrete event/state
 -> next action
```

## 11. Điều cần verify nếu implement cụ thể

- exact return type của `GetBuffs`;
- skill ID/template mapping trong Config bundle;
- built-in Auto Fight toggle/action method;
- exact server/client direction và payload của relevant commands;
- target validity and distance rules;
- cast/channel completion states.
