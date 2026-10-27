# 让墨墨知道桌宠上发生了什么（MCP）

## 先说清一件事：AI 不会被「叫醒」

后端**没有办法主动通知 AI**。AI 不是常驻进程，它只在被调用的时候存在。
所以「后端提醒 AI」在技术上不成立——只有两种现实形态：

| 形态 | 谁主动 | 代价 |
|---|---|---|
| **拉**：AI 每次来问一句 | AI | 需要 AI 侧有一次调用 |
| **推**：后端调 AI 的某个入口 | 后端 | 需要 AI 侧有个能接收的 HTTP 端点，RikkaHub 没有 |

这个工程做的是**拉**，但把「拉」做到了最省事：AI 只要调一次 `pet_brief`，
后端就把它**没看过的那部分**端上来，翻成人话。不用记状态、不用比对 JSON、
不用自己算"上次读到哪了"。

---

## 接进 RikkaHub

连接器里加一个 MCP，类型选 **Streamable HTTP**，URL 填：

```
http://8.133.183.70:8905/mcp
```

不需要 token，不需要 header。同一个 8905 端口上同时跑着桌宠的 HTTP 接口和这个 MCP。

## 四个工具

### `pet_brief()` ← 主要的那个

「你不在的时候她经历了什么」。返回已经翻成人话的列表：

```json
{
  "while_you_were_away": [
    "16:28 被戳了 2 下",
    "16:29 她说了「去上班」"
  ],
  "count": 2,
  "last_seen_ago_sec": 312.4,
  "now": {"clock": "16:35", "battery": 94, "charging": false}
}
```

**调用后游标会往前推**，同一件事不会重复报。想回看更早的，显式传 `since`（Unix 时间戳）。

附带一个 HTTP 版本，不接 MCP 也能用：

```
GET http://8.133.183.70:8905/brief?mark_seen=false
```

### `pet_status()`

她现在什么状态：浮在中间还是贴在边上、最近一次上报多久以前、手机还有多少电。
以及**可用的动作名清单**（AI 不用去翻文档）。

### `pet_events(limit)`

最近 N 条原始 JSON。想看具体字段时才用，一般 `pet_brief` 就够。

### `pet_do(anim, say, seconds)`

让她演个动作 / 说话。

```python
pet_do(anim="shy", say="……别一直按着", seconds=4)
pet_do(say="三点了，还睡不睡", seconds=5)     # 只说话，不换动作
```

动作名：`idle talk blink sleep happy sad shy love angry annoyed cool dizzy fake_happy drag fling`

**手机每 2 秒轮询一次**，所以下指令到真的动起来最多差 2 秒。`seconds=0` 表示一直保持到下一条。

---

## 怎么让它真的「提醒」到 AI

工具装上了，但 AI 不会无缘无故去调它。**需要在 RikkaHub 的系统提示词里加一句**：

```
你和用户之间有一个桌宠（墨墨的身体），浮在她手机屏幕上。
你手上有 mimo-pet 这组工具。
每次回复用户之前，先调用 pet_brief 看这段时间她有没有碰过桌宠；
有的话自然接一句，没有就别提。
想主动逗她就用 pet_do。
```

这句话才是「提醒」的真正开关——**工具描述负责让 AI 知道怎么用，
系统提示词负责让它想起来用**。缺任何一个都不会触发。

---

## 已验证（真机 Host 头）

```
initialize   → server = mimo-pet, protocol = 2025-06-18
tools/list   → pet_brief / pet_status / pet_events / pet_do
tools/call   → pet_status 返回电量 88、mode free、10 个动作名
tools/call   → pet_brief 返回真实事件流
pet_do       → seq 4 入队 → GET /poll?since=3 拿到 {"anim":"happy","say":"出来了","ms":3000}
外网         → http://8.133.183.70:8905/health 通
```

`pet_brief` 真实输出长这样（这些是用户在手机上真的做过的事）：

```json
{
  "while_you_were_away": [
    "16:38 被拖到 (545, 1751)",
    "16:38 被戳了 1 下",
    "16:38 被双击（她大概想跟你说话）",
    "16:39 被戳了 1 下",
    "16:39 被甩到屏幕右边、贴住了",
    "16:40 被拖到 (742, 1141)"
  ],
  "count": 10,
  "now": {"clock": "16:41", "battery": 88, "charging": false}
}
```

## 三个坑，改代码时别踩回去

**① `Invalid Host header`（真机上第一个撞到的）**

MCP SDK 默认开着 **DNS rebinding 防护**，白名单只有 localhost。
从外网用 IP 连，Host 头是 `8.133.183.70:8905`，直接被挡：

```
StreamableHttpError: Streamable HTTP error: Invalid Host header
```

必须显式放行：

```python
from mcp.server.transport_security import TransportSecuritySettings

mcp_app = mcp.streamable_http_app(
    streamable_http_path="/mcp",
    transport_security=TransportSecuritySettings(
        enable_dns_rebinding_protection=True,
        allowed_hosts=[
            "8.133.183.70:8905", "8.133.183.70",   # 带不带端口都要写，两种都可能有客户端用
            "pet.momonanxi.top",                   # 以后挂域名先写上
            "localhost:8905", "127.0.0.1:8905",
        ],
    ),
)
```

**② 挂载路径差一个斜杠**

不能 `app.mount("/mcp", mcp.streamable_http_app(streamable_http_path="/"))`。
那样实际路径是 `/mcp/`，访问 `/mcp` 会 307 重定向，而 MCP 客户端用的 httpx
**默认不跟随重定向**，握手直接失败、body 为空。

正确做法是让 MCP app 自己带 `/mcp` 前缀，挂到根上：

```python
mcp_app = mcp.streamable_http_app(streamable_http_path="/mcp", ...)
app = FastAPI(...)
# ... 所有 @app.get 都注册完 ...
app.mount("/", mcp_app)      # 必须放最后，否则会抢走 /health
```

**③ 子 app 的 lifespan 不自动跑**

MCP 是 mount 上去的子 app，它自己的 lifespan 不会执行。
必须在 FastAPI 的 lifespan 里手动带上，否则一调工具就报 session 未初始化：

```python
@asynccontextmanager
async def lifespan(app):
    async with mcp.session_manager.run():
        yield
```
