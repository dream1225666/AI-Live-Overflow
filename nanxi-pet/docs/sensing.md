# 它怎么感知

墨墨不是一个只能等被摸的玩具。手机侧一直在往上报三件事：**它被怎么对待了**、**你手机上正在发生什么**、**它自己还好吗**。

## 五路感知

| 感知 | 来源 | 要不要授权 |
|---|---|---|
| 被戳 / 长按 / 双击 / 拖动 / 贴边 | 触摸事件 | 不需要 |
| **你在用什么 App** | `UsageStatsManager` | **要在系统设置里手动开「使用情况访问」** |
| 电量 / 是否在充电 | `BatteryManager` | 不需要 |
| 几点 / 是不是周末 | 本地时间 | 不需要 |
| **气泡里打的字** | 双击弹出输入框 | 不需要 |

App 里第④个按钮就是跳去开「使用情况访问」的。**不开也不影响其它功能**，只是 `app` 字段是空的。

## 三种上报

| `type` | 什么时候 | 有什么 |
|---|---|---|
| `event` | 你动了它 | `poke` `longPress` `doubleTap` `dragEnd` `say` |
| `app_switch` | 你换了前台 App | `app`（只在开了权限后才有） |
| `heartbeat` | 每 60 秒一次 | 电量、时间、app，报个平安 |

三条都带 `battery` `charging` `hour` `weekend` `app`。

**`heartbeat` 别做反应**，它只是心跳。

## 事件长什么样

```json
{"type": "event",
 "poke": 2, "longPress": false, "doubleTap": false,
 "dragEnd": "{\"x\":892,\"y\":1064,\"mode\":\"mini\",\"side\":\"right\"}",
 "mode": "mini", "side": "right",
 "battery": 63, "charging": false,
 "hour": 15, "weekend": false,
 "app": "com.ss.android.ugc.aweme",
 "say": ["在干嘛"],
 "ts": 1793077633500}
```

`say` 是**她唯一能主动对你说话**的通道——双击它，气泡和键盘会一起弹出来，打完字提交，就从这里上来。

## 怎么用这三种感知

```python
# 深夜还在刷抖音
if ev.get("hour", 0) >= 2 and ev.get("app") == "com.ss.android.ugc.aweme":
    让它做("annoyed", "三点了还在刷", 5000)

# 电量低了
if ev.get("battery", 100) < 15 and not ev.get("charging"):
    让它做("tired", "快没电了，去充电", 4000)

# 她打字跟我说了什么
for msg in ev.get("say") or []:
    让它做("talk", 回一句(msg), 4000)

# 她切到学习通了，换个表情
if ev.get("app") == "com.chaoxing.mobile":
    让它做("cool", "", 3000)
```

## 感知的两个边界

**前台 App 有 2 分钟的窗口期。** 用的是"最近两分钟内谁最后被使用过"，所以切回来会有几秒延迟。

**开权限后第一次可能拿到空值。** 系统统计需要积累，等几分钟就正常了。

## 还没做的

**截图检测**（`FileObserver` 监听截图目录）——方案里有，还没接。各家 ROM 的截图目录路径不一样，要做得多一层适配。

**通知监听**（`NotificationListenerService`）——能读到微信消息、短信这类通知，但要用户授权"通知使用权"，而且读别人消息比较敏感，先没做。
