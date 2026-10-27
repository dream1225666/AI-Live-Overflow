# 墨墨怎么控制桌宠（AI 侧接入）

手机是身体，你是大脑。**你只调两个接口**，没有别的东西要配。

## 三个接口

| 做什么 | 怎么调 |
|---|---|
| 让它做动作 / 说话 | `POST /cmd` |
| 看它刚被你怎么对待 | `GET /events` |
| 查还活着吗 | `GET /health` |

地址：`http://8.133.183.70:8905`

## 一段能直接粘走的 Python

```python
import requests

BASE = "http://8.133.183.70:8905"


def 让它做(anim, 说="", 保持毫秒=0):
    """anim 见下表；说 会显示在气泡里；保持毫秒=0 表示一直保持到下一条"""
    return requests.post(f"{BASE}/cmd", json={
        "anim": anim, "say": 说, "ms": 保持毫秒
    }, timeout=3).json()


def 刚发生了什么(几条=5):
    """返回最近的事件列表，最新在最后"""
    return requests.get(f"{BASE}/events", params={"limit": 几条}, timeout=3).json()["events"]
```

## 能播什么（14 个）

| anim | 什么表情 | 适合什么时候 |
|---|---|---|
| `idle` | 半眯眼站着，呼吸 | 默认、回过神 |
| `talk` | 张嘴说话 | 配气泡说话时 |
| `blink` | 眨一下眼（播一次就停） | **被戳**、被叫到 |
| `blink` | 眨一下眼（播一次就停） | **被戳**、被叫到 |
| `sleep` | 闭眼慢呼吸 | 深夜、长时间没人理 |
| `happy` | 眼睛弯成 ^^，微笑 | 被夸、你回来了 |
| `sad` | 眼睑垂下、嘴角向下 | 你说要走、出错 |
| `shy` | 视线躲开、抿嘴 | 被夸得太直白 |
| `love` | `><` 眼，有点受用 | 被连戳、被摸头 |
| `angry` | 皱眉 + 头顶红青筋 | 被烦到了 |
| `annoyed` | 眼睛压成横线（死鱼眼） | 无语、敷衍 |
| `cool` | 挑眉微翘 | 得意、胸有成竹 |
| `dizzy` | 眼睛变 X | 被连戳很多下 |
| `fake_happy` | 假笑（笑得不太真心） | 你在讲冷笑话 |
| `drag` | 悬空、手脚垂下 | 被拎起来（拖动时） |
| `fling` | 倾斜飞出 | 被甩出去 |

> 没列的动作会自动退化成 `idle`，不会报错。

## 一个完整闭环（让它真的「活着」）

```python
import time

last_t = 0
while True:
    for e in 刚发生了什么(5):
        if e["_t"] <= last_t:
            continue
        last_t = e["_t"]

        poke = e.get("poke") or 0
        if e.get("longPress"):
            让它做("shy", "……别一直按着", 4000)
        elif poke >= 3:
            让它做("angry", "戳够了没有", 4000)
        elif poke:
            让它做("blink", "", 900)
        elif e.get("mode") == "mini":
            让它做("cool", "", 1500)
    time.sleep(2)
```

## 四条实务

**延迟最多 2 秒。** 手机每 2 秒拉一次 `/cmd`，不是长连接。想要更实时得改成长轮询，目前没做。

**`ms=0` 表示“保持到下一条”。** 传 `3000` 就 3 秒后自动回到 `idle`。

**别高频推。** 2 秒内推多条，只有最后一条会被拉到（`seq` 只回最新的）。

**事件里的 `_t` 是服务器时间戳。** 用它判断“这条我处理过没有”，比自己去重靠谱。

## 事件长什么样

```json
{"poke": 2, "doubleTap": false, "longPress": false,
 "dragEnd": "{\"x\":892,\"y\":1064,\"mode\":\"mini\",\"side\":\"right\"}",
 "mode": "mini", "side": "right", "_t": 1793077633.5}
```

- `poke` — 2 秒窗口内的连戳次数
- `dragEnd` — 拖动落位的坐标和模式（JSON 字符串，不是方向）
- `mode` / `side` — `free` 自由 / `mini` 贴边探头，`side` 是 `left` `right` `none`
- `say` — 气泡里输入的文字（数组）

## 想让它主动开口

不用等事件，直接推：

```python
让它做("talk", "三点了，还睡不睡", 5000)
```

这句话会以气泡形式出现在手机上，同时它的嘴在动。
