import base64, json, os, re

def _root(p):
    d = os.path.dirname(os.path.abspath(p))
    while d != os.path.dirname(d):
        if os.path.isdir(os.path.join(d, 'pet_frames')):
            return d
        d = os.path.dirname(d)
    raise SystemExit('找不到 pet_frames')


D = _root(__file__)
DIR = os.path.join(D, 'pet_frames', 'mimo')

FPS = {'idle': 3.85, 'talk': 5, 'happy': 5, 'angry': 6, 'sad': 4,
       'shy': 4, 'think': 4, 'sleep': 2, 'poke': 8, 'fling': 8}
LABEL = {'idle': '待机', 'talk': '说话', 'happy': '开心', 'angry': '不悦',
         'sad': '低落', 'shy': '害羞', 'think': '思考', 'sleep': '睡着',
         'poke': '被戳', 'fling': '被甩飞'}

cards = []
for f in sorted(os.listdir(DIR)):
    m = re.fullmatch(r'mimo_(\w+)\.png', f)
    if not m:
        continue
    name = m.group(1)
    b64 = base64.b64encode(open(os.path.join(DIR, f), 'rb').read()).decode()
    cards.append((name, b64))

if not cards:
    raise SystemExit('没有素材')

blocks = []
for name, b64 in cards:
    blocks.append(
        '<div class="cell"><div class="box"><canvas data-src="%s" data-fps="%s" '
        'width="64" height="64"></canvas></div>'
        '<div class="lbl">%s <span>%s</span></div></div>'
        % (b64, FPS.get(name, 5), LABEL.get(name, name), name))

html = """<!doctype html><html lang="zh"><head><meta charset="utf-8">
<title>墨墨动作预览</title>
<style>
*{box-sizing:border-box}
body{margin:0;font:14px/1.6 -apple-system,"Segoe UI",system-ui,sans-serif;
  background:#f6f4f0;color:#2c2c2a;display:flex;flex-direction:column;align-items:center;
  padding:26px 20px 40px}
h1{font-size:15px;font-weight:500;margin:0 0 4px}
.sub{font-size:12px;color:#8b8880;margin:0 0 18px}
.bar{display:flex;gap:8px;margin:0 0 22px}
button{background:#fff;border:1px solid #dcd8d0;border-radius:8px;padding:6px 14px;
  font:inherit;font-size:12px;cursor:pointer}
button.on{background:#2d3a2f;border-color:#5b9e6a;color:#fff}
.row{display:flex;gap:16px;flex-wrap:wrap;justify-content:center;max-width:860px}
.cell{display:flex;flex-direction:column;align-items:center;gap:6px}
.box{width:190px;height:190px;border-radius:14px;background:#1a1917;
  display:flex;align-items:center;justify-content:center;overflow:hidden;transition:background .2s}
canvas{width:190px;height:190px;image-rendering:pixelated;image-rendering:crisp-edges}
.lbl{font-size:11px;color:#8b8880}
.lbl span{color:#b4b2a9;font-family:ui-monospace,Consolas,monospace}
</style></head><body>
<h1>墨墨 · 已完成动作</h1>
<p class="sub">64×64 · 每格独立循环 · 点下面换底色看效果</p>
<div class="bar">
  <button data-bg="dark" class="on">深色</button>
  <button data-bg="light">浅色</button>
  <button data-bg="wall">花壁纸</button>
</div>
<div class="row">__CARDS__</div>
<script>
var boxes = [].slice.call(document.querySelectorAll('.box'));
document.querySelectorAll('button').forEach(function (b) {
  b.onclick = function () {
    document.querySelectorAll('button').forEach(function (x) { x.classList.remove('on'); });
    b.classList.add('on');
    var bg = b.dataset.bg;
    var v = bg === 'dark' ? '#1a1917' : bg === 'light' ? '#f6f4f0'
      : 'repeating-linear-gradient(45deg,#c9d6e3 0 14px,#e8eef4 14px 28px)';
    boxes.forEach(function (x) { x.style.background = v; });
  };
});
document.querySelectorAll('canvas').forEach(function (cv) {
  var img = new Image();
  var g = cv.getContext('2d');
  g.imageSmoothingEnabled = false;
  var fps = parseFloat(cv.dataset.fps) || 5, fi = 0, n = 1;
  img.onload = function () {
    n = Math.max(1, Math.round(img.naturalWidth / img.naturalHeight));
    (function step() {
      g.clearRect(0, 0, 64, 64);
      g.drawImage(img, fi * 64, 0, 64, 64, 0, 0, 64, 64);
      fi = (fi + 1) % n;
      setTimeout(step, 1000 / fps);
    })();
  };
  img.src = cv.dataset.src;
});
</script></body></html>"""

html = html.replace('__CARDS__', '\n'.join(blocks))
open(os.path.join(DIR, 'preview.html'), 'w', encoding='utf-8').write(html)
print('preview.html 已生成，%d 个动作：%s' % (len(cards), ', '.join(n for n, _ in cards)))
