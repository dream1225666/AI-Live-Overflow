# 南兮桌宠（Nanxi Pet）

按 [AI-Live-Overflow](https://github.com/Vael-KY/AI-Live-Overflow) 的「大脑 / 身体分离」思路搭的 Android 悬浮桌宠。
素材用 [operit-clawd](https://github.com/watersalt0305/operit-clawd) 的像素精灵图，悬浮窗宿主用它的 `ClawdHost.java`（改成我们的包名）。

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

## 编译

本机不装 Android SDK，靠 GitHub Actions：

```bash
git init && git add -A && git commit -m "init"
git remote add origin git@github.com:<你>/<仓库>.git
git push -u origin main
```

push 后去 Actions 页下载 `nanxi-pet-debug` artifact。

## 已知状态

- 渲染层已本地验证：canvas 32×32 → 窗口内 320×320，`transform: none`，螃蟹正常绘制。
- 后端已端到端跑通：上报 → 读 → 下指令 → 轮询取 → 不重复消费。
- **整个工程还没真编译过**（本机无 Android SDK，VPS 1.6G 内存跑不动 Gradle）。第一次 CI 可能要修一两个编译错误。
- 手势视觉反馈由 `ClawdHost` 内部直接调 `window.clawd(...)` 完成，触摸方已经能用；上报后端是为了让大脑知道。

## 协议

- 素材与 `ClawdHost.java` 来自 operit-clawd，**AGPL-3.0**。自用无约束；公开发布需整体以 AGPL 开源署名。
  形象是 Claude Code 吉祥物 Clawd，上游标注非官方粉丝作品。
- 架构思路来自 AI-Live-Overflow，**CC BY-NC-SA 4.0**，不可商用。
