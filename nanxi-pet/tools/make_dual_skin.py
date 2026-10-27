"""把 pet.html 改成双皮肤：clawd（32×32，68 张）与 mimo（64×64，14 个动作）。

可重复执行：已改过的文件再跑一次会更新 mimo 表，不会叠加。
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
    'blink': ('mimo_blink.png', 10),
    'sleep': ('mimo_sleep.png', 1.5),
    'happy': ('mimo_happy.png', 5),
    'sad': ('mimo_sad.png', 4),
    'shy': ('mimo_shy.png', 4),
    'love': ('mimo_love.png', 4),
    'angry': ('mimo_angry.png', 5),
    'annoyed': ('mimo_annoyed.png', 5),
    'cool': ('mimo_cool.png', 4),
    'dizzy': ('mimo_dizzy.png', 6),
    'fake_happy': ('mimo_fake_happy.png', 4),
    'drag': ('mimo_drag.png', 4),
    'fling': ('mimo_fling.png', 8),
}

# pet.html 里会用到的状态名 → 复用哪个动作（墨墨没做的动作就近退化）
MIMO_ALIAS = {
    'mini_idle': 'idle', 'edge_idle': 'idle', 'mini_peek': 'idle', 'look': 'idle',
    'edge_look': 'idle', 'mini_crabwalk': 'idle',
    'doze': 'sleep', 'bubble': 'sleep', 'collapse': 'sleep',
    'mini_sleep': 'sleep', 'edge_sleep': 'sleep', 'mini_enter_sleep': 'sleep',
    'edge_doze': 'sleep', 'edge_bubble': 'sleep', 'sleep_bubble': 'sleep',
    'error': 'sad', 'edge_error': 'sad', 'bash_err': 'sad', 'edge_bash_err': 'sad',
    'notify': 'annoyed', 'poke_huh': 'annoyed', 'edge_poke_huh': 'annoyed',
    'edge_annoyed': 'angry', 'edge_notify': 'annoyed',
    'wake': 'annoyed', 'edge_wake': 'annoyed',
    'poke_hit': 'blink', 'left': 'love', 'right': 'love', 'edge_love': 'love',
    'double_jump': 'happy', 'mini_happy': 'happy', 'edge_happy': 'happy',
    'edge_shy': 'shy', 'edge_dizzy': 'dizzy', 'edge_double_jump': 'happy',
    'drop': 'drag', 'dock': 'drag', 'mini_enter': 'drag', 'mini_slide': 'drag',
}


def mimo_table():
    base = {k: [{'src': 'sprites_mimo/' + f, 'fps': fps}] for k, (f, fps) in MIMO.items()}
    base['blink'][0]['loop'] = False   # 眨一下就好，停住别反复眨
    for alias, target in MIMO_ALIAS.items():
        base[alias] = base[target]
    return base


def main():
    s = open(PET, encoding='utf-8').read().replace('\r\n', '\n')
    mimo_json = json.dumps(mimo_table(), ensure_ascii=False, separators=(',', ':'))

    if 'var SPR_CLAWD' in s:
        # 已经是双皮肤版：只更新 mimo 表
        s2 = re.sub(r'var SPR_MIMO = \{.*?\};\nvar SKINS',
                    'var SPR_MIMO = ' + mimo_json + ';\nvar SKINS', s, count=1, flags=re.S)
        if s2 == s:
            print('⚠️ SPR_MIMO 没被替换，检查格式')
        else:
            open(PET, 'w', encoding='utf-8').write(s2)
            print('SPR_MIMO 已更新：%d 个状态' % len(mimo_table()))
        return

    head = 'var SPR  = '
    i = s.index(head)
    j = s.index('};', i)
    clawd_json = s[i + len(head):j + 1]
    tail = s[j + 2:]

    block = ('var SPR_CLAWD = ' + clawd_json + ';\n'
             'var SPR_MIMO = ' + mimo_json + ';\n'
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

    old_play = 'function play(name, restart) {\n  if (SPR[name]) {'
    new_play = ('function play(name, restart) {\n'
                '  if (!SPR[name] && SPR.idle) name = "idle";\n'
                '  if (SPR[name]) {')
    if old_play in s:
        s = s.replace(old_play, new_play, 1)

    open(PET, 'w', encoding='utf-8').write(s)
    print('pet.html 已改为双皮肤 %.1fKB' % (len(s) / 1024))
    print('  clawd 状态数:', len(json.loads(clawd_json)))
    print('  mimo  状态数:', len(mimo_table()))


if __name__ == '__main__':
    main()
