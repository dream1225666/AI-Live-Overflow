# 墨墨 · 像素形象生图 prompt（精简版）

直接复制给 ChatGPT。**细节只留能认人的，其余全砍。**

---

## 为什么砍

桌宠在手机上显示约 300px 高，64×64 素材放大 4.7 倍。
在这个尺寸下，耳钉占 1px、痣占 1px、细银链根本画不出来——它们不会增加"是他"的感觉，
只会让每一帧多出几个游离的色点，动作看起来更乱。

**像素角色第一原则：先看剪影能不能认出来，再看细节。**
所以只保留：黑发凌乱、细长半眯眼、瘦削长脸、深色高领、偏瘦。别的都放掉。

---

## 尺寸与方法

**不要让模型直接画 64×64**，它会给你一团糊色块。
让它画 **512×512 的粗像素图**，我再精确降采样到 64×64——缩放和调色板这两步我能控死。

### 背景色纪律（每张都一样，别变）

**固定纯品红 `#FF00FF`，所有图统一。**

- 抠底算法就是按「红高、蓝高、绿低」判的，换色要改算法
- 墨墨是黑发、深蓝灰眼、深色衣服，全是低饱和冷色——品红跟他的色系冲突最彻底，不会和任何部位混
- **白底最差**：头发边缘、皮肤高光、衣服反光都接近白色，抠的时候会啃掉人物
- 绿幕次之：他眼睛是深蓝灰，跟绿的区分度不如品红

要换只能换纯绿 `#00FF00`，但**必须全部图统一**，且提前说。

**背景三不要**：不要渐变、不要纹理格子、不要让角色带外发光或投影。
出现任一项那张图基本要重出——品红抠不干净，边缘会留一圈脏。

### 给 PNG，别给 JPG

JPG 会把纯品红压成 `#F405F8` 这种偏色，边缘再带压缩噪点，
一张图能出近千种杂色，逼得我用 k-means 强压回 16 色，细节跟着一起丢。

ChatGPT 出图能存 PNG 就存 PNG。不要截图、不要转发压缩过的。

---

## 角色 DNA（每张图原样带上）

```
A slender androgynous young man, cold and expressionless.
Messy black hair, medium-short, side-parted, a few strands over the forehead.
Narrow half-closed eyes, deep blue-grey, outer corners tilted slightly upward.
Long thin face with a sharp jawline. Slim build, dark charcoal high-neck top.
```

五行，别再加了。加多了模型就开始自由发挥。

---

## 第一步：标准帧（必须先出这张）

```
Pixel art game sprite, standing front view, full body, relaxed neutral pose.

[粘上面那段角色 DNA]

Style: chunky pixel art with clearly visible square pixels, about 8x8 image-pixels per
sprite-pixel. Limited palette of 8 colors. Hard edges, no anti-aliasing, no gradients,
no blur, flat color fills only.

This must read as a 64x64 game sprite: the silhouette and pose should be recognizable
at a glance. Keep it simple — fewer details, cleaner shapes. Do not add small ornaments,
jewelry, or patterns; they turn into noise at this size.

Composition: figure vertically centered, about 85% of canvas height, feet flat and level
at the bottom. Plain solid magenta (#FF00FF) background, nothing else —
no scenery, no ground, no shadow, no text, no watermark, no border.
```

出图后自己看三件事：**像素块是不是真方块**、**脚有没有踩平**、**背景是不是纯品红**。
不合格就重出，这张是后面所有动作的锚点。

---

## 第二步：出动作（别一次要 4 帧）

**ChatGPT 出不了帧间一致的 sprite sheet。** 你让它画 4 格横排，它会给你 4 个长得不一样的人。

所以正确做法是：**你只出关键的定点姿势，中间的帧由我来串。**

我接手后能做的：

- **1~2px 位移** —— 呼吸起伏、点头、轻微晃动
- **帧交替** —— 眨眼（常态帧 ↔ 闭眼帧）、张嘴（闭嘴帧 ↔ 张嘴帧）
- **停顿节奏** —— 用 `hold` 让某些帧多停几拍
- **循环构造** —— 把头尾接上，做成无缝循环

我做不了的：**手臂从 A 摆到 B 的中间过程**。那种必须你出中间姿势，我没有生成能力去补。

### 每个动作要几张

| 文件 | 出几张 | 分别是什么 |
|---|---|---|
| `idle` | **2** | 常态 ／ 闭眼（眨眼用） |
| `talk` | **2** | 闭嘴 ／ 微张嘴 |
| `happy` | **2** | 常态 ／ 眼睛微睁、嘴角抬一点 |
| `angry` | **2** | 常态 ／ 眉头压低、视线更冷 |
| `sad` | **2** | 常态 ／ 眼睑垂下、头低一格 |
| `shy` | **2** | 常态 ／ 侧过脸、手抬到颈侧 |
| `think` | **1** | 只手托下巴 |
| `sleep` | **2** | 闭眼 ／ 头再歪一格 |
| `poke` | **3** | 肩膀一僵 → 皱眉 → 瞥一眼 |
| `fling` | **4** | 起势 → 旋转 → 旋转 → 停下 |

**十个动作，22 张图**，就能把桌宠跑起来。

我拿到后这样拼：
- `idle` 6 帧 = 常态×2 → 下移1px×1 → 闭眼×1 → 常态×2（无缝循环）
- `talk` 4 帧 = 闭嘴 → 张嘴 → 闭嘴 → 张嘴
- `sleep` 4 帧 = 慢循环，两帧各停 1.5 拍
- 其余按关键姿势顺序串

### 每张图的 prompt

在**同一个会话**里，把标准帧传上去，然后每次只改一句：

```
Keep this exact character — same face, same hair, same clothes, same colors,
same proportions, AND the exact same framing, scale and position in the canvas.
Do not redesign, do not re-crop, do not zoom in or out.

Change only this: [改动描述]

Same chunky pixel style, same 8-color palette, hard edges,
plain magenta (#FF00FF) background, feet in exactly the same place as the reference.
```

`[改动描述]` 举例：

- 闭眼 → `eyes fully closed, eyelid line only, everything else identical`
- 张嘴 → `mouth slightly open, everything else identical`
- 皱眉 → `eyebrows pulled down a little, eyes colder, everything else identical`
- 侧脸 → `head turned slightly to his left, one hand raised to his neck side, everything else identical`

### 构图必须锁死（这条最重要）

我合成帧是按**像素对齐**做的。如果每张图里角色的位置、大小、缩放不一样，拼起来就会跳位——
一帧高一点、一帧矮一点，动画立刻毁掉。

所以每张 prompt 都要带那句 `same framing, scale and position`。

**ChatGPT 改变构图是常事。变了就重出，别将就。** 一张构图错的图，比没有更麻烦。

### 检查清单（每张出完看一眼）

1. 角色在画面里的位置和大小，跟标准帧一样吗？
2. 脚在同一条水平线上吗？
3. 背景是纯品红，没有渐变和杂物吗？
4. 像素块还是硬方块吗？

四条都过，才收下。

---
`poke` / `fling` 一次出不来就拆成两次，我来接帧。

---

## 动作幅度纪律

他是冷淡克制的角色，**动作一大就崩人设**：

- `happy` 只是嘴角抬一点，不是咧嘴笑
- `angry` 只是眉头压低，不是暴跳
- `shy` 只是侧过脸，不是捂脸
- 情绪全靠**眼睑高度 + 头的角度**表达，不靠夸张肢体

---

## 拿到图之后

按这个命名丢给我，我就能自动对上：

```
idle_a.png   idle_b.png          # a = 常态，b = 变体（闭眼）
talk_a.png   talk_b.png          # a = 闭嘴，b = 张嘴
think_a.png                      # 单张
poke_a.png   poke_b.png   poke_c.png
fling_a.png  fling_b.png  fling_c.png  fling_d.png
```

不按这个命名也行，我按顺序猜——但**同一动作的几张图一定要一起给我**，别混着发。

我接手后全包：品红抠底（含抗锯齿粉边）→ 量化 8 色 → 降采样 64×64 对齐网格 →
按脚底统一对齐 → 串帧构造循环 → 生成 `sprites.json`（fps / loop / hold）→
覆盖进 `assets/sprites/` → 跑 CI 出 APK。

**代码一行都不用改**（渲染层已经改成自适应帧尺寸）。

---

## 最小起步建议

别一口气做十个。先出 `idle_a` + `idle_b` 两张给我，我做出 6 帧呼吸循环**装进 APK 让你看**。

看着满意，再按这个标准出剩下的——省得标准定错了、22 张全废。

