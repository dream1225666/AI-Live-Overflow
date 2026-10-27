"""把 pet.html 改成双皮肤：clawd（32×32，68 张）与 mimo（64×64，逐步补齐）。

可重复执行：已经改过的文件再跑一次也不会叠加。
"""
import json
import os
import re
import sys

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PET = os.path.join(D, 'app', 'src', 'main', 'assets', 'pet.html')

MIMO = {
    'idle': ('mimo_idle.png', 3.85),
    'talk': ('mimo_talk.png', 5),
    'sleep': ('mimo_sleep.png', 1.5),
}
MIMO_ALIAS = {
    'mini_idle': 'idle', 'edge_idle': 'idle', 'mini_peek': 'idle', 'look': 'idle',
    'doze': 'sleep', 'bubble': 'sleep', 'collapse': 'sleep',
    'mini_sleep': 'sleep', 'edge_sleep': 'sleep', 'mini_enter_sleep': 'sleep',
}


def mimo_table():
    base = {k: [{'src': 'sprites_mimo/' + f, 'fps': fps}] for k, (f, fps) in MIMO.items()}
    for alias, target in MIMO_ALIAS.items():
        base[alias] = base[target]
    return base


def main():
    s = open(PET, encoding='utf-8').read().replace('\r\n', '\n')

    if 'var SPR_CLAWD' in s:
        print('已经是双皮肤版，跳过')
        return

    head = 'var SPR  = '
    i = s.index(head)
    j = s.index('};', i)
    clawd_json = s[i + len(head):j + 1]
    tail = s[j + 2:]

    block = ('var SPR_CLAWD = ' + clawd_json + ';\n'
             'var SPR_MIMO = ' + json.dumps(mimo_table(), ensure_ascii=False, separators=(',', ':')) + ';\n'
             'var SKINS = { clawd: SPR_CLAWD, mimo: SPR_MIMO };\n'
             'var SPR = SPR_CLAWD;\n'
             'var skinName = "clawd";\n'
             'window.setSkin = function (k) {\n'
             '  if (!SKINS[k]) k = "clawd";\n'
             '  skinName = k; SPR = SKINS[k];\n'
             '  cur = null; sp.img = null; sp.v = null; sp.f = 0; sprCache = {};\n'
             '  try { cv.width = 32; cv.height = 32; cx = cv.getContext("2d"); '
             'cx.imageSmoothingEnabled = false; } catch (e) {}\n'
             '  rest();\n'
             '};\n'
             'window.getSkin = function () { return skinName; };\n')
    s = s[:i] + block + tail

    # 缺失的动作回退到 idle，避免墨墨皮肤下点到没有的动作就卡住
    old_play = 'function play(name, restart) {\n  if (SPR[name]) {'
    new_play = ('function play(name, restart) {\n'
                '  if (!SPR[name] && SPR.idle) name = "idle";\n'
                '  if (SPR[name]) {')
    if old_play in s:
        s = s.replace(old_play, new_play, 1)
    else:
        print('⚠️ play() 结构与预期不同，未加 fallback')

    open(PET, 'w', encoding='utf-8').write(s)
    print('pet.html 已改为双皮肤 %.1fKB' % (len(s) / 1024))
    print('  clawd 状态数:', len(json.loads(clawd_json)))
    print('  mimo  状态数:', len(mimo_table()))


if __name__ == '__main__':
    main()
