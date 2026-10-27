# 墨墨桌宠 · 手机身体

墨墨从对话框里伸出来的一小块，蹲在手机上。南兮是它的人类。
这个 App 是**身体**——显示、感知、上报；人格和记忆不在这里。

按 [AI-Live-Overflow](https://github.com/Vael-KY/AI-Live-Overflow) 的「大脑 / 身体分离」思路搭的。
素材与悬浮窗宿主 `ClawdHost.java` 来自 [operit-clawd](https://github.com/watersalt0305/operit-clawd)（改了包名）。

## 分工

```
大脑（你的 AI）  ──POST /cmd──▶  VPS 后端  ──GET /poll──▶  手机（身体）
                 ◀──GET /events──           ◀──POST /event──
```

手机只负责「显示 + 感知 + 上报」，人格和记忆留在你自己的 AI 那边。

## 目录

```
app/src/main/
  java/top/momonanxi/pet/
    ClawdHost.java        悬浮窗宿主，901 行纯 android.* API（上游移植，改了包名）
    PetOverlayService.kt  前台服务：喂页面、收手势、拉指令
    MainActivity.kt       权限引导 + 启停
    BootReceiver.kt       开机自启
  assets/
    pet.html              渲染层：91 个状态 → 139 个素材引用
    bubble.html           对话气泡
    sprites/              68 张 32×32 横排雪碧图
server/
  main.py                 FastAPI 状态总线（零数据库，内存 + JSON 落地）
  nanxi-pet.service       systemd 单元
.github/workflows/
  build.yml               push 即出 APK
```

## 后端

已部署：`http://8.133.183.70:8905`（systemd 服务名 `nanxi-pet`，端口 8905）

| 端点 | 用途 |
|---|---|
| `POST /event` | 手机上报：戳了几下、双击、长按、甩飞、输入的文字 |
| `GET /events?limit=N` | 大脑读：她刚被怎么对待了 |
| `POST /cmd` | 大脑写：`{"anim":"happy","say":"...","ms":3000}` |
| `GET /poll?since=SEQ` | 手机轮询取指令，`since` 之上才返回，取过不重复 |
| `GET /health` | 活着没 |

`anim` 取值见 `assets/pet.html` 里的 `SPR` 表（`happy` `shy` `angry` `sad` `think` `typing` `fling` `sleep` …），
`ms=0` 表示一直保持到下一条。

## 怎么联动

两个方向都是普通 HTTP，没有长连接、没有 WebSocket。

**手机 → 后端**（已自动在跑）
手机每 2 秒问一次「有没有要我做的」：`GET /poll?since=<seq>`。
被戳 / 长按 / 双击 / 拖 / 在气泡里打字时，`POST /event` 推上去。

**后端 → 手机**（你或墨墨主动推）

```bash
curl -X POST http://8.133.183.70:8905/cmd \
  -H 'Content-Type: application/json' \
  -d '{"anim":"happy","say":"我在这","ms":4000}'
```

手机下次轮询就播，**最慢 2 秒**。`ms=0` 表示一直保持到下一条指令。

**墨墨怎么知道被戳了**

```bash
curl 'http://8.133.183.70:8905/events?limit=5'
```

返回最近的事件，形如：

```json
{"poke": 2, "doubleTap": false, "longPress": false,
 "dragEnd": "{\"x\":892,\"y\":1064,\"mode\":\"mini\",\"side\":\"right\"}",
 "mode": "mini", "side": "right", "_t": 1793077633.5}
```

- `poke` — 2 秒窗口内的连戳次数
- `longPress` / `doubleTap` — 长按 / 双击
- `dragEnd` — 拖动结束时的**落位坐标和模式**（JSON 字符串，不是方向）
- `mode` / `side` — `free` 自由悬浮 / `mini` 贴边探头，`side` 是 `left` `right` `none`
- `say` — 在气泡里输入的文字（数组）

### 先看闭环跑通

`server/echo_bot.py` 是个纯规则的「笨版墨墨」，不接模型：

```bash
python3 server/echo_bot.py
```

跑起来后戳桌宠，她两秒内会回话。接真正的墨墨时，只把 `react()` 那几行规则换成模型调用，
两头（读 `/events`、写 `/cmd`）原样不动。

### 能播什么

`anim` 取值见 `app/src/main/assets/pet.html` 里的 `SPR` 表，常用的：

| 想表达 | anim |
|---|---|
| 开心 / 讨好 | `happy` |
| 害羞 / 被摸 | `shy` `love` |
| 生气 / 被戳烦了 | `angry` `annoyed` |
| 难过 / 出错 | `sad` `error` |
| 疑惑 | `notify` `confused` |
| 思考 | `think` |
| 说话 | `talk` |
| 睡觉 / 打盹 | `sleep` `doze` |
| 敲键盘 / 干活 | `typing` `building` `debugger` |
| 甩飞 | `fling` |

## 下载安装

APK 直链（每次 push 自动重建、覆盖同一个地址）：

```
https://github.com/dream1225666/AI-Live-Overflow/releases/download/latest-build/app-debug.apk
```

装好后：桌面点「南兮」→ 授予**悬浮窗权限** → 点「让南兮出来」。

## 编译

本机不装 Android SDK，靠 GitHub Actions。工程在 `nanxi-pet/` 子目录，
workflow 在**仓库根目录**的 `.github/workflows/build-apk.yml`（GitHub 只认根目录），
用 `defaults.run.working-directory: nanxi-pet` 指定构建目录。

push 后自动出 APK 并发布到 Release（tag `latest-build`），也可以在 Actions 页下 artifact。

## 已知状态

- 渲染层已本地验证：canvas 32×32 → 窗口内 320×320，`transform: none`，螃蟹正常绘制。
- 后端已端到端跑通：上报 → 读 → 下指令 → 轮询取 → 不重复消费。
- **CI 已构建成功**（run 40445651754），APK 3.2MB。
- 尚未在真机上安装验证。手势视觉反馈由 `ClawdHost` 内部直接调 `window.clawd(...)` 完成；
  上报后端是为了让大脑知道发生了什么。

## 协议

- 素材与 `ClawdHost.java` 来自 operit-clawd，**AGPL-3.0**。自用无约束；公开发布需整体以 AGPL 开源署名。
  形象是 Claude Code 吉祥物 Clawd，上游标注非官方粉丝作品。
- 架构思路来自 AI-Live-Overflow，**CC BY-NC-SA 4.0**，不可商用。
