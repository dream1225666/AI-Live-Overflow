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

## 第二步：出动作

标准帧**作为参考图上传**，然后一个动作一个 prompt：

```
Keep this exact character — same face, same hair, same clothes, same colors,
same proportions, same silhouette. Do not redesign.

Change only the pose: [动作描述]

Same chunky pixel style, same 8-color palette, same hard edges,
same plain magenta (#FF00FF) background, feet level at the bottom.
```

### 动作表（帧数已经按流畅度压过了）

| 文件名 | 帧数 | 动作描述 |
|---|---|---|
| `idle` | 6 | 呼吸，肩膀起伏 1 格，第 4 帧眨一次眼 |
| `talk` | 4 | 只有嘴动，微张 → 闭合 |
| `happy` | 4 | 半眯的眼睛微睁，嘴角抬一点点（他很克制，不要笑开） |
| `angry` | 4 | 眉头压低，视线更冷，肩膀绷紧 |
| `sad` | 4 | 眼睑垂下，头低 1 格 |
| `shy` | 4 | 侧过脸，一只手抬到颈侧 |
| `think` | 4 | 一只手托下巴，眼睛看斜上方 |
| `sleep` | 4 | 闭眼，头微歪，呼吸幅度变小 |
| `poke` | 6 | 被戳：肩膀一僵 → 皱眉 → 瞥一眼 |
| `fling` | 8 | 被甩出：身体旋转，速度线，撞边缘停住 |

**48 帧封顶。** 帧数越多动作越碎，反而更不流畅——像素动画靠的是"少而准的姿势"。

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

丢给我，全包：品红抠底 → 量化 8 色 → 降采样 64×64 对齐网格 → 按脚底对齐切帧 →
生成 `sprites.json` → 覆盖进 assets → 跑 CI 出 APK。

文件名和帧数按上表来，**代码一行都不用改**（渲染层已经改成自适应尺寸）。
