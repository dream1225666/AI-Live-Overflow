"""
墨墨桌宠的「身体」后端。

极简共享数据层：手机把摸到它的事件推上来，大脑（墨墨）读走；
墨墨想做动作/说话，就推一条指令下来，手机 2 秒内轮询拿到。

零数据库，全靠内存 + 一个 JSON 文件落地，重启不丢最近状态。
"""
import json
import os
import time
from collections import deque
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

STATE_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "state.json")

app = FastAPI(title="Nanxi Pet Body")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)

# 环形缓冲只留 40 条：墨墨是每 2 秒轮询的，永远读不到历史。
# 40 条只用来兜住「连戳十几下 / 两秒内多件事」的密集交互，再多纯属浪费内存和落盘 IO。
EVENTS: deque = deque(maxlen=40)
CMDS: deque = deque(maxlen=20)
_seq = 0
_last: Dict[str, Any] = {}
_save_at = 0.0


def _load():
    global _seq
    try:
        with open(STATE_FILE, encoding="utf-8") as f:
            d = json.load(f)
        for e in d.get("events", [])[-EVENTS.maxlen:]:
            EVENTS.append(e)
        for c in d.get("cmds", [])[-CMDS.maxlen:]:
            CMDS.append(c)
        _seq = int(d.get("seq", 0))
    except Exception:
        pass


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
                {"events": list(EVENTS), "cmds": list(CMDS), "seq": _seq},
                f, ensure_ascii=False,
            )
    except Exception:
        pass


_load()


@app.get("/health")
def health():
    return {"ok": True, "seq": _seq, "events": len(EVENTS)}


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

    # 心跳只用来更新「最近一次听到它」的快照，不占事件队列。
    # 否则 300 条的环形缓冲会被心跳慢慢填满，真实交互反而被挤出去。
    if body.get("type") != "heartbeat":
        EVENTS.append(body)
        _save()
    return {"ok": True, "n": len(EVENTS)}


@app.get("/events")
def events(limit: int = 10):
    """大脑来读：她刚被怎么对待了。默认给最近 10 条就够。"""
    n = max(1, min(limit, EVENTS.maxlen or 1))
    return {"events": list(EVENTS)[-n:]}


@app.post("/cmd")
async def cmd(req: Request):
    """大脑来写：让她播个动作 / 说句话。"""
    global _seq
    try:
        body: Dict[str, Any] = await req.json()
    except Exception:
        body = {}
    _seq += 1
    item = {
        "seq": _seq,
        "anim": str(body.get("anim", "") or ""),
        "say": str(body.get("say", "") or ""),
        "ms": int(body.get("ms", 0) or 0),
        "_t": time.time(),
    }
    CMDS.append(item)
    _save()
    return item


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


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8905)
