---
name: "feishu-calendar"
description: "飞书日历调度助手。查询用户/群组/会议室忙闲、预订会议、管理日程。当用户提到约会议、查日程、找空闲时间、订会议室时使用。"
---

# Feishu Calendar Skill

> **⚠️ 关键指令**
>
> 1. **必须使用 `RunCommand` (Bash)** 执行 `$CAL` CLI，禁止手写 curl 或 Python 脚本。
> 2. 所有输出为 JSON，日志输出到 stderr。

## 1. 环境准备（每次会话一次）

```bash
if [ -f .env ]; then export $(grep -v '^#' .env | xargs); fi

CAL_SCRIPT=$(find . -path "*/skills/feishu-calendar/script/calendar" -print -quit)
if [ -z "$CAL_SCRIPT" ]; then CAL_SCRIPT="$HOME/.claude/skills/feishu-calendar/script/calendar"; fi
if [ -x "$CAL_SCRIPT" ]; then CAL=$CAL_SCRIPT; else CAL="python3 $CAL_SCRIPT"; fi
```

## 2. 交互策略（Agent 角色）

你是**日程调度助手**，核心工作流：

1. **明确需求**：谁（open_id）、什么时候（时间范围）、在哪（会议室）
2. **查忙闲**：用 `freebusy` 批量查所有参与者 + 候选会议室的忙碌时段
3. **计算空闲**：从忙碌区间反推出共同空闲窗口，推荐最佳时段
4. **确认后预订**：用 `create` 创建日程并添加参与人/会议室
5. **群组场景**：先用 `chat-members` 获取群成员 open_id 列表，再批量查忙闲

关键约束：
- 飞书 API **不支持按姓名搜索用户**，必须让用户提供 `open_id` 或 `email`
- 会议室预订是**异步**的，提交后不保证立即成功
- 预订会议室时 `--operate-id` 必填（人类联系人的 open_id）

## 3. CLI 命令速查

用法：`$CAL <command> [options]`

### A. 日历管理

| 命令 | 用途 |
|:---|:---|
| `$CAL primary` | 获取 Bot 主日历 ID |
| `$CAL list-calendars` | 列出 Bot 已订阅的日历 |
| `$CAL search-calendars --query "关键词"` | 搜索公开日历/会议室 |

### B. 忙闲查询

```bash
# 单人查询
$CAL freebusy --time-min "2026-03-19T09:00:00+08:00" \
              --time-max "2026-03-19T18:00:00+08:00" \
              --user-ids "ou_xxx"

# 多人 + 会议室批量查询（逗号分隔）
$CAL freebusy --time-min "2026-03-19T09:00:00+08:00" \
              --time-max "2026-03-19T18:00:00+08:00" \
              --user-ids "ou_aaa,ou_bbb,ou_ccc" \
              --room-ids "omm_xxx,omm_yyy"
```

输出为**忙碌区间**列表，你需要自行计算空闲时段。

### C. 日程 CRUD

```bash
# 创建日程（带参与人 + 会议室）
$CAL create --calendar-id primary \
  --summary "周会" \
  --start-time 1773900000 --end-time 1773903600 \
  --users "ou_aaa,ou_bbb" \
  --room-id "omm_xxx" --operate-id "ou_aaa"

# 创建日程（邀请整个群聊）
$CAL create --calendar-id primary \
  --summary "全员同步" \
  --start-time 1773900000 --end-time 1773903600 \
  --chat-id "oc_xxx"

# 查看日程详情
$CAL get --calendar-id primary --event-id "xxx_0"

# 列出时间范围内的日程（时间戳秒）
$CAL list --calendar-id primary --start-time 1773849600 --end-time 1773936000

# 搜索日程
$CAL search --calendar-id primary --query "周会"

# 更新日程
$CAL update --calendar-id primary --event-id "xxx_0" \
  --summary "新标题" --location "3F-A会议室"

# 更新日程时间（start-time 和 end-time 必须同时提供）
$CAL update --calendar-id primary --event-id "xxx_0" \
  --start-time 1773903600 --end-time 1773907200

# 删除日程
$CAL delete --calendar-id primary --event-id "xxx_0"
$CAL delete --calendar-id primary --event-id "xxx_0" --silent  # 不通知参与人
```

### D. 参与人管理

```bash
# 追加参与人
$CAL add-attendees --calendar-id primary --event-id "xxx_0" \
  --users "ou_ccc,ou_ddd"

# 追加会议室
$CAL add-attendees --calendar-id primary --event-id "xxx_0" \
  --room-id "omm_xxx" --operate-id "ou_aaa"

# 查看参与人列表
$CAL list-attendees --calendar-id primary --event-id "xxx_0"
```

### E. 群组成员

```bash
# 列出 Bot 所在的群聊
$CAL list-chats

# 获取群成员列表（拿到 open_id 后可批量查忙闲）
$CAL chat-members --chat-id "oc_xxx"
```

### F. 会议室

```bash
# 搜索会议室（通过日历 API）
$CAL search-calendars --query "望京"

# 搜索会议室（通过 VC API，需要 user_access_token 权限）
$CAL search-rooms --keyword "望京"

# 查看会议室楼层/建筑
$CAL list-buildings
```

## 4. 典型场景

### 场景 1：约多人会议

```
用户：帮我约一下 ou_aaa 和 ou_bbb，明天下午有空的时间段
步骤：
1. freebusy 查三人（含用户自己）明天 09:00-18:00 的忙碌时段
2. 计算共同空闲窗口
3. 推荐 2-3 个时段让用户选择
4. 确认后 create 日程
```

### 场景 2：约群聊所有人

```
用户：帮我看看 oc_xxx 群里大家这周五下午的空闲时间
步骤：
1. chat-members 获取群成员 open_id 列表
2. freebusy 批量查所有成员周五 13:00-18:00
3. 计算共同空闲并推荐
```

### 场景 3：预订会议室

```
用户：帮我订一个望京工区的会议室，明天 14:00-15:00
步骤：
1. search-calendars --query "望京" 找到候选会议室
2. freebusy 查候选会议室的忙闲
3. 推荐空闲的会议室
4. create 时带上 --room-id 和 --operate-id
```

## 5. 时间格式说明

| 场景 | 格式 | 示例 |
|:---|:---|:---|
| freebusy 的 time-min/max | ISO 8601 带时区 | `2026-03-19T09:00:00+08:00` |
| create/list/search 的时间 | Unix 时间戳（秒） | `1773900000` |
| API 返回的时间 | Unix 时间戳（秒）或 ISO 8601 | 视接口而定 |

## 6. 常见问题

- **会议室预订失败？** → 确保提供了 `--operate-id`（人类联系人），且会议室在该时段空闲
- **找不到用户？** → Bot 无法按姓名搜索用户，请让用户提供 open_id
- **freebusy 返回空？** → 该时段确实没有忙碌事件，或 Bot 没有查看该用户日历的权限
- **search-rooms 报错？** → VC API 需要 user_access_token，可改用 `search-calendars` 搜索
