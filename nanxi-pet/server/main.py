"""
墨墨桌宠的「身体」后端。

极简共享数据层：
  手机 → POST /event     被摸到了
  墨墨 → GET  /events    她刚被怎么对待了
  墨墨 → GET  /brief     人话摘要（自上次以来发生了什么）
  墨墨 → POST /cmd       让她演个动作 / 说句话
  手机 → GET  /poll      取指令

同一个服务上还挂了 MCP：/mcp —— 墨墨在 RikkaHub 里能直接当工具调。

零数据库，内存 + 一个 JSON 文件落地，重启不丢最近状态。
"""
import json
import os
import time
from collections import deque
from contextlib import asynccontextmanager
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from mcp.server.mcpserver import MCPServer

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

# 环形缓冲只留 10 条：墨墨是每 2 秒轮询的，永远读不到历史。
EVENTS: deque = deque(maxlen=10)
CMDS: deque = deque(maxlen=10)
_seq = 0
_last: Dict[str, Any] = {}
_save_at = 0.0
# /brief 的游标：上次「读到哪儿了」。用来只端出没看过的那些。
_brief_at = 0.0


def _load():
    global _seq, _brief_at
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        for e in d.get("events", [])[-EVENTS.maxlen:]:
            EVENTS.append(e)
        for c in d.get("cmds", [])[-CMDS.maxlen:]:
            CMDS.append(c)
        _seq = int(d.get("seq", 0))
        # 重启后不要一上来就把旧事件当成「你不在时发生的」
        _brief_at = float(d.get("brief_at", time.time()))
    except Exception:
        _brief_at = time.time()


def _save(force: bool = False):
    """落盘节流：最短 3 秒写一次。连戳十下不必写十次盘。"""
    global _save_at
    now = time.time()
    if not force and now - _save_at < 3:
        return
    _save_at = now
    try:
        with open(STATE_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "events": list(EVENTS),
                    "cmds": list(CMDS),
                    "seq": _seq,
                    "brief_at": _brief_at,
                },
                f,
                ensure_ascii=False,
            )
    except Exception:
        pass


def _push_cmd(anim: str, say: str, ms: int) -> Dict[str, Any]:
    global _seq
    _seq += 1
    item = {
        "seq": _seq,
        "anim": str(anim or ""),
        "say": str(say or ""),
        "ms": int(ms or 0),
        "_t": time.time(),
    }
    CMDS.append(item)
    _save()
    return item


def _describe(e: Dict[str, Any]) -> List[str]:
    """把一条原始事件翻成人话。翻不出东西就返回空列表（心跳之类）。"""
    if e.get("type") == "heartbeat":
        return []
    bits: List[str] = []
    poke = e.get("poke") or 0
    if poke:
        bits.append("被戳了 %d 下" % poke)
    if e.get("longPress"):
        bits.append("被长按了")
    if e.get("doubleTap"):
        bits.append("被双击（她大概想跟你说话）")
    de = e.get("dragEnd")
    if de:
        try:
            d = json.loads(de) if isinstance(de, str) else de
            if d.get("mode") == "mini":
                side = "左" if d.get("side") == "left" else "右"
                bits.append("被甩到屏幕%s边、贴住了" % side)
            else:
                bits.append("被拖到 (%s, %s)" % (d.get("x"), d.get("y")))
        except Exception:
            bits.append("被拖动过")
    for msg in e.get("say") or []:
        bits.append("她说了「%s」" % msg)
    return bits


def _brief(mark_seen: bool, since: Optional[float] = None) -> Dict[str, Any]:
    """自上次以来发生了什么。"""
    global _brief_at
    base = _brief_at if since is None else float(since)
    now = time.time()
    fresh = [e for e in EVENTS if float(e.get("_t", 0)) > base]

    lines = []
    for e in fresh:
        bits = _describe(e)
        if not bits:
            continue
        hhmm = time.strftime("%H:%M", time.localtime(float(e.get("_t", now))))
        lines.append("%s %s" % (hhmm, "，".join(bits)))

    latest = fresh[-1] if fresh else (_last or {})
    out: Dict[str, Any] = {
        "while_you_were_away": lines,
        "count": len(lines),
        "last_seen_ago_sec": round(now - base, 1),
        "now": {
            "clock": time.strftime("%H:%M", time.localtime(now)),
            "hour": latest.get("hour"),
            "battery": latest.get("battery"),
            "charging": latest.get("charging"),
        },
    }
    if not lines:
        out["hint"] = "这段时间她没被碰过。想主动找她就用 pet_do。"
    if since is not None and mark_seen:
        _brief_at = now
        _save()
    elif mark_seen:
        _brief_at = now
        _save()
    return out


_load()

# ======================= MCP（给墨墨的工具） =======================

ANIMS = (
    "idle talk blink sleep happy sad shy love angry annoyed cool dizzy fake_happy drag fling"
)

mcp = MCPServer(
    "mimo-pet",
    instructions=(
        "这是墨墨桌宠的身体。她在用户手机屏幕上浮着。\n"
        "用户碰她（戳、长按、双击、拖动、在气泡里打字）时后端会记下来。\n"
        "想知道用户刚才对她做了什么，调 pet_brief——它只给你没看过的那些。\n"
        "想让她有反应（演动作、说话），调 pet_do。"
    ),
)


@mcp.tool()
def pet_brief(since: Optional[float] = None) -> Dict[str, Any]:
    """看看你不在的时候，用户对她做了什么。

    这是最该先调用的一个。返回自上次调用以来发生的互动，已经翻成人话，
    比如「16:28 被戳了 2 下，她说了「去上班」」。同时带上当前电量和时钟。

    调用之后游标会往前推，所以同一件事不会重复报给你。
    想重看更早的，就显式传 since（Unix 时间戳）。
    """
    return _brief(mark_seen=True, since=since)


@mcp.tool()
def pet_status() -> Dict[str, Any]:
    """她现在什么样：浮在屏幕中间还是贴在边上、最近一次上报是什么时候。"""
    now = time.time()
    return {
        "last_event_ago_sec": (
            round(now - float(_last.get("_t", now)), 1) if _last else None
        ),
        "last": _last or None,
        "mode": (_last or {}).get("mode"),
        "side": (_last or {}).get("side"),
        "battery": (_last or {}).get("battery"),
        "charging": (_last or {}).get("charging"),
        "queue": {"events": len(EVENTS), "cmds": len(CMDS)},
        "available_anims": ANIMS.split(),
    }


@mcp.tool()
def pet_events(limit: int = 10) -> Dict[str, Any]:
    """最近 N 条原始事件（JSON），需要看具体字段时才用，一般用 pet_brief 就够。"""
    n = max(1, min(int(limit or 10), EVENTS.maxlen or 1))
    return {"events": list(EVENTS)[-n:]}


@mcp.tool()
def pet_do(anim: str = "", say: str = "", seconds: int = 0) -> Dict[str, Any]:
    """让她在手机屏幕上做点反应。

    anim:    动作名。可选：idle talk blink sleep happy sad shy love angry
             annoyed cool dizzy fake_happy drag fling。留空就只说话不说话。
    say:     气泡里显示的话。留空就只做动作，不弹气泡。
    seconds: 保持几秒。0 = 一直保持到下一条指令。

    手机每 2 秒轮询一次，所以最多 2 秒后才会动起来。
    """
    if not anim and not say:
        return {"error": "anim 和 say 至少给一个"}
    item = _push_cmd(anim, say, int(seconds or 0) * 1000)
    return {"ok": True, "queued": item, "note": "手机最多 2 秒后来取"}


# ======================= HTTP =======================

# 注意：不能用 app.mount("/mcp", ...) + streamable_http_path="/"。
# 那样实际路径是 /mcp/，访问 /mcp 会被 307 重定向到 /mcp/，
# 而 MCP 客户端（httpx）默认不跟随重定向，握手直接失败。
# 所以让 MCP app 自己带 /mcp 前缀，挂到根上；FastAPI 已注册的路由会先匹配。
mcp_app = mcp.streamable_http_app(streamable_http_path="/mcp", stateless_http=True)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # MCP 被 mount 成子 app，它自己的 lifespan 不会自动跑，这里手动带上
    async with mcp.session_manager.run():
        yield


app = FastAPI(title="Mimo Pet Body", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
# mount 放在所有路由之后（见文件末尾）


@app.get("/health")
def health():
    return {"ok": True, "seq": _seq, "events": len(EVENTS), "mcp": "/mcp"}


@app.post("/event")
async def event(req: Request):
    """手机端推上来的手势 / 输入 / 心跳。"""
    global _last
    try:
        body = await req.json()
    except Exception:
        body = {"raw": (await req.body()).decode("utf-8", "ignore")}
    body["_t"] = time.time()
    _last = body

    # 心跳只更新快照，不占事件队列，否则真实交互会被挤出去
    if body.get("type") != "heartbeat":
        EVENTS.append(body)
        _save()
    return {"ok": True, "n": len(EVENTS)}


@app.get("/events")
def events(limit: int = 10):
    """大脑来读：她刚被怎么对待了。默认给最近 10 条就够。"""
    n = max(1, min(limit, EVENTS.maxlen or 1))
    return {"events": list(EVENTS)[-n:]}


@app.get("/brief")
def brief(since: Optional[float] = None, mark_seen: bool = True):
    """人话摘要：自上次以来发生了什么。不接 MCP 也能用。"""
    return _brief(mark_seen=mark_seen, since=since)


@app.post("/cmd")
async def cmd(req: Request):
    """大脑来写：让她播个动作 / 说句话。"""
    try:
        body: Dict[str, Any] = await req.json()
    except Exception:
        body = {}
    return _push_cmd(
        str(body.get("anim", "") or ""),
        str(body.get("say", "") or ""),
        int(body.get("ms", 0) or 0),
    )


@app.get("/poll")
def poll(since: int = 0):
    """手机端轮询：有没有要播的。"""
    for c in reversed(CMDS):
        if c["seq"] > since:
            return c
    return {}


@app.get("/state")
def state():
    return {"last": _last, "seq": _seq, "pending": len(CMDS)}


# 所有 HTTP 路由都注册完了，最后再把 MCP 挂到根上，避免它抢走 /health 之类的路径
app.mount("/", mcp_app)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8905)
