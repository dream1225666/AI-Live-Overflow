"""
最小闭环示例：轮询事件 → 决定反应 → 推回指令。

这是个「笨版墨墨」——纯规则，不接 LLM。跑起来之后你戳桌宠，
两秒内她就会回话，证明整条链路是通的。

用法：
    python3 echo_bot.py                      # 连默认后端
    BACKEND=http://... python3 echo_bot.py   # 换后端

接入真正的墨墨时，把这个「规则判断」部分换成你的模型调用就行，
两头（读 /events、写 /cmd）不用改。
"""
import json
import os
import time
import urllib.request

BACKEND = os.environ.get("BACKEND", "http://8.133.183.70:8905")


def get(path):
    req = urllib.request.Request(BACKEND + path, headers={"User-Agent": "echo-bot"})
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def post(path, body):
    data = json.dumps(body).encode()
    req = urllib.request.Request(
        BACKEND + path, data=data, headers={"Content-Type": "application/json"}
    )
    with urllib.request.urlopen(req, timeout=5) as r:
        return json.loads(r.read())


def react(ev):
    """一条事件 → 一条反应。这里就是「墨墨的性格」所在的位置。

    可用的 anim（墨墨皮肤）：idle talk blink sleep happy sad shy love angry
    annoyed cool dizzy fake_happy drag fling
    """
    kind = ev.get("type")
    # 心跳 / 换 app / 插拔充电：只是背景信息，别吭声
    if kind in ("heartbeat", "app_switch", "charging_on", "charging_off"):
        return None

    poke = ev.get("poke") or 0
    # 气泡里打的字 —— 她主动说的话
    said = ev.get("say") or []
    if said:
        return {"anim": "talk", "say": "「%s」……嗯。" % said[0], "ms": 4000}
    if ev.get("longPress"):
        return {"anim": "shy", "say": "……别一直按着", "ms": 4000}
    if ev.get("doubleTap"):
        return {"anim": "talk", "say": "我在。", "ms": 5000}
    if poke >= 3:
        return {"anim": "angry", "say": "戳够了没有", "ms": 4000}
    if poke == 2:
        return {"anim": "annoyed", "say": "？", "ms": 2500}
    if poke == 1:
        return {"anim": "blink", "ms": 900}
    if ev.get("dragEnd"):
        # 拖动只是搬家。只有贴到屏幕边缘（mode 变 mini）才哼一声
        if ev.get("mode") == "mini":
            return {"anim": "cool", "ms": 1500}
        return None
    return None


def main():
    print("连", BACKEND, "——戳一下桌宠试试")
    last_t = 0.0
    while True:
        try:
            evs = get("/events?limit=5").get("events", [])
            for ev in evs:
                t = ev.get("_t", 0)
                if t <= last_t:
                    continue
                last_t = t
                cmd = react(ev)
                if cmd:
                    post("/cmd", cmd)
                    print("%.0f  %s  ->  %s" % (t, ev, cmd.get("say", "")))
        except KeyboardInterrupt:
            print("\n走了")
            return
        except Exception as e:
            print("网络问题:", e)
        time.sleep(2)


if __name__ == "__main__":
    main()
