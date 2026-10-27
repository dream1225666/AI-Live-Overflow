# 墨墨表情 · 可直接复制的 prompt（全正脸版）

**用法**：同一个 ChatGPT 会话里，先把 `idle_a`（睁眼那张）当参考图传上去，
  
然后一条条复制下面的 prompt 发出去。每段都是完整的，不用自己加任何东西。

**存 PNG，不要截图。**

---

## 两条总纪律

**一、全部正脸。** 头必须正对镜头，不许侧转、不许歪头、不许低头抬头。

原因很实际：侧转在 64px 下会糊成一团，而且每张侧的角度都不太一样，合成循环时会跳。
  
正脸还有个好处——所有表情都靠「眼睛 + 眉毛 + 嘴」三样说话，识别度高、一致性稳。

**二、必须是 Q 版比例。** 头约占身高一半，身体短、腿短。
  
这一条最容易丢：一旦让 AI 画「悬空」「跳起」「被甩」这类动作，它会自动把身体拉成瘦长条，
  
看起来像换了个成年人。所以每段 prompt 里都写死 `CHIBI proportions — head about half his
total height, short compact body, short legs`，并且加一句 `do not make him taller or slimmer`。

**关于「正脸」的边界**：正脸是给**表情**定的——脸上的东西必须朝前，否则几张图对不上。
  
但**姿态不需要对称**。悬空、被甩这类动作，脖子以下要松掉：身体微微后仰、两臂一高一低、
  
一条腿弯一条直。**对称是僵硬的根源**，真实的重力从来不均匀。
  
表情类动作（happy/sad/angry…）全身静止不动；姿态类动作（drag/fling）脸朝前、身体放开。

情绪不用藏着。之前我把幅度压成 1 像素，结果几个表情互相看不出区别，等于白做。
  
**该笑就笑，该垮就垮。**

---

## 1 · happy　开心

眼睛微弯，嘴角明显上扬。这个可以看得出在笑。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: he is genuinely pleased. His narrow eyes curve into gentle upward
arcs, and his mouth is a clear, soft smile — the corners lifted noticeably, not just a pixel.
Keep it restrained in style but readable as a smile.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 2 · annoyed　无语 ★

眼睛压成一条横线（死鱼眼），嘴压成更短的线。被你说傻话时的表情。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: utterly unimpressed. His eyes are flattened into thin horizontal
lines — almost dead-fish eyes, no visible pupil highlight. His mouth is compressed into a short
flat line, shorter than usual. Brows level.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 3 · sad　低落

眉毛内侧上挑，眼睛下垂，嘴角向下。头不动。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt, no lowering.

Change only the expression: downcast. His eyebrows tilt upward in the middle, his eyelids droop
so the eyes look heavier and lower, and his mouth is a small curve bending downward at the corners.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 4 · angry　不悦

眉毛压成倒八字，眼睛变窄，嘴抿成短横，**头顶右上方浮一个红色青筋符号**（贴着头发，不能飘远）。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: clearly irritated. His eyebrows are pressed down and angled inward
like a shallow V, his eyes narrowed and sharp, and his mouth pulled into a short tight line.
The mood is annoyed and sulky, not screaming.

Also add one small comic anger mark floating just above the upper-right side of his head, sitting
close to the hair: the classic four-stroke anger vein symbol, drawn in flat red, in the same chunky
pixel style and the same pixel size as the character. Make it about the size of one of his eyes.
Leave only a thin gap between the symbol and the hair — it must sit right next to the head, not
float away, and must not overlap his face.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 5 · shy　害羞

眼睛**完全不动**，只有瞳孔偏向下方；两侧脸颊各加**2~3 道短斜线腮红**（不是实心块）；嘴抿成一条细短的线。头不动。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt, no turning away.

Change only the expression: shy. The eyes must stay EXACTLY as they are in the reference — same
narrow shape, same eyelid height, same amount of visible iris, same white of the eye. Do not close
them, do not blur them, do not merge them into a flat shape. The only change is the pupils, which
shift to look down and to one side, as if he cannot meet your eyes.
On each cheek add a light blush made of two or three SHORT DIAGONAL STROKES in a pale warm pink,
placed high on the cheekbone just under the eye. They must read as thin separate pixel strokes —
NOT a solid filled circle, NOT a large patch, and they must not cover or blur the face outline.
His mouth becomes a single short thin slightly tense horizontal line. Keep his original narrow eye
shape.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 6 · think　思考

眼睛看向斜上方，一边眉毛略抬。头不动。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: thinking it over. His pupils are shifted up and to one side as if
looking at something above, one eyebrow raised slightly higher than the other, mouth a small flat
line. No hand gesture needed.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 7 · sleep　睡着 ✗ 不用生成

**直接复用 `idle_b`（闭眼那张）。** 闭眼帧本身就是睡着的样子，只靠极慢的呼吸就够区分：

```
帧序 = [闭眼, 闭眼下沉1px, 闭眼下沉2px, 闭眼下沉1px]  @ 1.5fps
```

已经做好了（`mimo_sleep.png`），省一张图。

---

## 8 · surprise　惊讶

眼睛变成圆的，嘴小圆张开。这是可以夸张的那个。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: caught off guard. His narrow eyes are opened wider than usual — more
of the blue-grey iris showing than in any other expression — brows lifted, and his mouth a small
open oval. Keep the narrow eye shape; do not turn the eyes into circles unless the widened narrow
version reads poorly at this size.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 9 · tired　疲惫

眼睑压到最沉，眼下有一道浅色，嘴一条线。头不动。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt, no drooping.

Change only the expression: worn out. His eyelids hang at their heaviest, covering most of the
eye, with a faint shadow beneath them. Mouth a single flat line. Shoulders dropped slightly.
Drained rather than sad.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

---

## 10 · dizzy　晕

眼睛变成两个叉或两个小漩涡，嘴是小波浪。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: woozy and dazed. His eyes are drawn as two small X shapes,
and his mouth is a small wavy line. He looks light-headed, not angry. Do not add blush or red
patches on the cheeks.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```


## 出完之后

按 `<表情名>.png` 命名发给我（`happy.png`、`annoyed.png`…），一批一起给。

我会统一处理：锁 bbox 裁切 → alpha 预乘缩放 → 16 色量化 → 和 `idle_a` 配对成循环 →
  
生成 `mimo_<名字>.png` → 更新预览页 → 一起打进 APK。

**某张脸型变了 / 头发变了 / 头歪了 / 构图移了，直接重出那张，别发给我。**

---

## 还需要哪些动作（表情之外）

表情只解决「脸上的事」。桌宠要像活的，还有**身体的事**——而且这部分比表情更影响观感。

### 必须的（缺了会明显穿帮）

| 动作              | 为什么必须                                       | 要几张 |
| --------------- | ------------------------------------------- | --- |
| `drag` **被拎起来** | **现在拖他的时候还是站着的**，像拽一块纸板。这是目前最明显的缺口          | 1   |
| `fling` **被甩飞** | 甩出去要有姿态，不能平移                                | 2   |
| `wake` **醒来**   | 从睡着切到任何状态，没有过渡就是硬切                          | 1   |
| `poke` | 比平时**紧一点点**（1~2px） | 平线压紧一丝 | 保留 |

### 有趣但不急的

| 动作           | 效果                | 备注                                      |
| ------------ | ----------------- | --------------------------------------- |
| `look` 东张西望  | 空闲时随机做，立刻显得在「看着你」 | 只动瞳孔，1 张                                |
| `yawn` 打哈欠   | 深夜时段专用，配合睡眠状态     | 和 wake 可以共用                             |
| `dizzy` 晕    | 被连戳太多时            | 1 张，叉眼                                  |
| `typing` 敲键盘 | AI 干活时切换          | **Q 版手太短，敲键盘很难画**。建议改成「抱着一个小方块」，比敲键盘好表达 |
| `dock` 贴边探头  | 拖到屏幕边缘            | 需要专门的斜靠姿态                               |

### 不用生成的

这些我用代码就能做，别浪费额度：

- **眨眼** —— `idle_b` 插一帧，已在用
- **睡眠** —— `idle_b` + 1~2px 慢呼吸，已做好
- **呼吸** —— `idle_a` 上下位移
- **落地** —— 位移 + `fling` 的最后一帧

---

## 建议的生成顺序

**第一批（4 张）**：`drag` → `fling` → `wake` → `poke`
  
身体动作先补齐，这比多十种表情更能让人觉得「这是个活物」。

**第二批（4 张）**：`happy` → `annoyed` → `shy` → `sad`
  
常用的四种情绪。

**第三批（看心情）**：`confused` → `angry`（带青筋）→ `think` → `tired` → `dizzy` → `surprise`

`surprise` 留到最后，只用于**真的被吓到**的场合（突然的通知、闹钟、你猛地凑近）。

---

## 第一批的四段 prompt

### drag · 被拎起来

**目前最明显的缺口**：现在拖他的时候身体还站着，像拽一块纸板。

⚠️ **别写「被谁拎着」**。写 `lifted by the collar` 这类描述，AI 会把施力的手一起画进来。
  
拖着桌子上的他时，那只手是你自己的，画面里绝不能有。**只描述他现在的样子：悬空、手脚垂下。**

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the pose: he is dangling in mid-air, loose and off-balance.
His body hangs slightly backward as gravity pulls his feet down. Nothing about the pose is
symmetrical — one arm hangs a little looser and lower than the other, one knee bends slightly while
the other leg stays straight, one shoulder sits a touch higher.
His face still looks straight out at the viewer with the head level, but everything below the neck
is limp and uneven, like a small thing actually dangling from a hand.
His legs stay SHORT and chibi exactly as in the reference — do not lengthen them, do not make his
body longer. The hem of his top is lifted a little, and his hair falls downward a touch.

IMPORTANT — do not draw any hand, arm, hook, rope or object holding him up. Nothing may appear
above his head or touching him. He hangs in empty space on his own; whoever is holding him is
outside the frame and invisible.
Keep his body proportions exactly as in the reference — do not stretch, elongate, thin out or
squash him. The hair keeps the same shape as the reference.
Expression stays the same neutral half-lidded look — mildly inconvenienced, not scared.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Plain solid magenta (#FF00FF) background, nothing else.
No text, no shadow, no glow, no motion lines.
```

### fling · 被甩出去

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.

Change only the pose: he is tumbling through the air sideways. His whole body is tilted about
30 degrees away from vertical, arms and legs trailing behind him in the direction he came from,
his hair pushed slightly against the motion. Expression: eyes a little wider than usual, mouth
slightly open, off balance.

IMPORTANT — do not draw any hand, arm, foot or object of any kind besides him. Nothing else may
appear in the frame. Do not add motion lines or speed streaks; they turn into noise at this size.
Keep his body proportions exactly as in the reference.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Plain solid magenta (#FF00FF) background, nothing else.
No text, no shadow, no glow.
```

### wake · 醒来

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the pose and expression: he has just snapped awake. Both eyes are now open — wider than
his usual half-closed state, but with the eyelids still a little heavy. Brows slightly lifted.
Mouth a small open oval. His body is pulled up straight with the shoulders raised a touch, as if he
was caught slouching. Still a bit dazed, not alarmed.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

### poke · 被戳（几乎没变的那一版）

**他被人戳了一下，只是眼睛本能地紧了一点。** 不要 `><`、不要笑、不要脸红、不要弹开——
那些是萌系表达，跟他不是一路人。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: he felt that. A small involuntary squint — his narrow eyes press
slightly tighter than in the reference, no more than a pixel or two, as if something just touched
him. His mouth stays a flat line, pressed a touch tighter. Nothing else changes: no squeezed-shut
eyes, no upward >< shape, no smile, no blush, no head tilt, no body movement.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```

> 如果连这个都觉得夸张，那就**根本不用出图**——我直接在代码里给他加一个 1px 的抖动
> （被碰了一下，整个人轻轻一颤），眼睛完全不变。这个效果最像「活人被戳」，而且零素材成本。

### confused · 疑惑（另做，不是被戳用）

被戳用上面那张。这张留给**你说傻话**的时候——挑眉看你一眼，意思是「你在讲什么」。

```
Same character as the reference image — same face shape, same messy black side-parted hair,
same dark charcoal high-neck top, same CHIBI proportions — head about half his total height,
short compact body, short legs, same colors. Do not redesign, do not make him taller or slimmer.
Head faces straight forward, no tilt.

Change only the expression: mildly puzzled. One eyebrow is raised noticeably higher than the other.
His narrow eyes shift to look directly outward at the viewer, as if asking "what do you want".
His mouth stays a flat line, maybe tilted a hair to one side.
His body stays completely relaxed and upright — no flinching, no hunched shoulders, no leaning back,
no startled reaction. He is not surprised. He is just mildly bothered that you did that.

Pixel art, chunky visible square pixels, limited 8-color palette, hard edges, no anti-aliasing,
no gradients, no blur. Same framing, same scale, same position in the canvas as the reference —
do not re-crop, do not zoom in or out. Feet flat at the bottom. Plain solid magenta (#FF00FF)
background, nothing else. No text, no shadow, no glow.
```
