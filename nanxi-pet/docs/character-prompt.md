# 墨墨形象 · 像素生图规格书

给 ChatGPT 用。分两步走：**先定一张标准帧，再基于它出动作**。
一次生成整张 sprite sheet 的成功率不高，但如果规格讲得够死，是可以试的。

---

## 0. 硬规格（不管谁来画，这几条不能变）

| 项 | 要求 | 为什么 |
|---|---|---|
| 单帧尺寸 | **32 × 32 px** | 现有渲染层按 32×32 画布写死 |
| 排布 | **横排**，帧数 = 图宽 ÷ 32 | 播放器按 `naturalWidth / naturalHeight` 算帧数 |
| 格式 | PNG，**背景填纯品红 `#FF00FF`** | 模型做不出真透明，品红抠得最干净 |
| 角色高度 | 26px 左右，**脚底贴格子底部** | 切换动作时不跳位 |
| 边缘 | 硬边、无抗锯齿、无半透明过渡 | 像素风一糊就废 |
| 禁止 | 阴影、地面、投影、文字、水印、多余装饰 | 抠图和后续对齐都会被干扰 |
| 调色 | 全角色 ≤ 12 色 | 越少越像素，也越好对齐 |

⚠️ **别让模型填"透明背景"**。它会画成白底或棋盘格，反而更难抠——品红是最优解。

---

## 1. 先定角色 DNA（这段每张图都要原样带上）

形象你自己定，但描述必须**固定不变**。扩散模型每次都会自由发挥，
唯一能压住它的办法是把"长什么样"写成一段模板，每张 prompt 一字不差地重复。

### 模板

```
A [整体形态]，[主体颜色]，[眼睛的样式]，[标志性特征 1]，[标志性特征 2]。
像素艺术，32×32 网格，硬边，无抗锯齿，纯色平涂，仅用 8 种颜色。
```

### 三个方向（挑一个改，或完全自己想）

**A. 墨滴** —— 名字叫墨墨，最贴
> A small ink blob creature, deep blue-black with a violet sheen, two large round white eyes with tiny pupils, a single ink droplet hanging off its bottom edge, tiny stubby arms. 像素艺术，32×32 网格……

**B. 纸团**
> A crumpled paper ball creature, warm off-white with soft grey creases, two oval black eyes, one folded corner that acts like an ear, no legs (floats). 像素艺术……

**C. 小机器人**
> A palm-sized robot, matte grey body with a single amber glowing eye slit, two thin antennae, blocky limbs. 像素艺术……

选好后把那段英文学死，后面每个动作都带上。

---

## 2. 第一步：标准帧（必须先出这张）

```
Pixel art sprite, 32x32 pixel grid, single frame, front-facing neutral standing pose.
[这里粘你的角色 DNA]
Centered horizontally, feet touching the bottom edge of the grid, about 26 pixels tall,
soft magenta (#FF00FF) solid background filling everything else.
Hard pixel edges, no anti-aliasing, no gradients, no outline blur, no shadow, no ground,
no text, no watermark. Flat colors only, maximum 8 colors.
The image must look like it was drawn pixel-by-pixel on a 32x32 canvas, then scaled up
with nearest-neighbor so every pixel is a visible square.
```

出图后检查三件事：**是不是硬边方块**、**脚有没有贴底**、**背景是不是纯品红**。
不合格就重出，别将就——这张是后面所有动作的锚点。

---

## 3. 第二步：出动作

出完标准帧，**把标准帧作为参考图上传**，然后一个动作一个 prompt：
（ChatGPT 里直接说「保持这个角色的形象完全不变，只改姿势」）

```
Same character, same style, same colors, same 8-color palette — do not redesign.
New pose: [动作描述]
32x32 pixel grid, character feet on the bottom edge, soft magenta (#FF00FF) background.
Hard pixel edges, no anti-aliasing, no shadow, no text.
Horizontal sprite sheet, [N] frames side by side, each frame the same 32x32 size,
the character must keep identical proportions, colors and silhouette width in every frame.
```

### 要哪些动作

**P0 · 十个就够她活起来**

| 文件名 | 帧数 | 动作描述（填进上面 `[动作描述]`） |
|---|---|---|
| `idle` | 8 | 站着呼吸，身体上下 1px 起伏，中途眨一次眼 |
| `talk` | 4 | 嘴一张一合，其他不动 |
| `happy` | 4 | 眼睛弯成 ^^，轻轻跳一下 |
| `angry` | 4 | 皱眉，头顶冒一小团气，身体微微抖 |
| `sad` | 4 | 眼睛下垂，低头，肩膀塌下来 |
| `shy` | 6 | 脸红，身体侧过去一点，手抬到脸边 |
| `think` | 4 | 一只手托住下巴，眼睛往上看 |
| `sleep` | 4 | 闭眼，身体缩起来，慢慢呼吸 |
| `poke` | 9 | 被戳：一惊 → 眼睛变 >< → 抖两下 → 恢复 |
| `fling` | 12 | 被甩出去：身体旋转，带速度线，最后撞墙停住 |

**P1 · 有这些才像活人**（先不急）

`typing`(8) 敲键盘　`drag`(4) 被拎起来手脚悬空　`drop`(6) 落地弹一下　
`dock`(6) 贴到屏幕边缘停下　`notify`(8) 吓一跳　`confused`(6) 一脸问号　
`reading`(8) 看书　`building`(8) 搬东西

> 帧数是我按现有 `sprites.json` 抄的。如果模型一次出不了这么多帧，
> **出 2~4 帧也行**，剩下的我用 1px 位移和停顿补出来，但会少点灵性。

---

## 4. 拿到图之后我做什么

你只要把 PNG 丢给我，剩下的我全包：

1. 品红抠底 → 去掉所有 #FF00FF 及抗锯齿边缘
2. 量化到 ≤12 色调色板（防止半透明糊边）
3. **对齐 32×32 网格**：按脚底对齐 + 水平居中，保证切动作不跳位
4. 按帧宽自动切帧，生成新的 `sprites.json`（fps / loop / hold）
5. 重命名成现有文件名，直接覆盖进 `assets/sprites/`
6. 跑一次 CI，出新 APK

所以**文件名和帧数尽量按上表来**，代码一行都不用改。

---

## 5. 两个现实提醒

**模型做 pixel-perfect 的 32×32 很难。** 它会给 33px、会给你画成 512×512、
会让第 3 帧的眼睛突然变成 1 像素。所以：

- 第一张标准帧**必须**卡死，后面全靠它做参考图
- sprite sheet 一次出 4 帧成功率还行，出 9~12 帧（poke / fling）基本要靠拆成两三次
- 出歪了我能修（对齐、调色、补帧），但**帧与帧之间形象不一致**是修不了的，只能重出

**如果试了几轮都不行**，还有两条退路：

- 我拿标准帧本地做程序化动画（上下 1px 呼吸、眨眼换一张闭眼版、抖动靠位移），能凑出 idle / talk / happy / angry / sad / shy / sleep
- 动作复杂的（fling / poke / typing）再单独攻，或者干脆砍掉

先出标准帧。那张定了，剩下的都是它的变体。
