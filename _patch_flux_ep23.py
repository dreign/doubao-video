"""用第02、03集的模块覆盖 shots_flux 里的旧 9 镜映射（R/COMP/LIGHT 三处一致）。"""
import re, io

p = r"D:\AAA\text\假钦差\短剧\shots_flux.py"
src = open(p, encoding="utf-8").read()

# 1) R / COMP / LIGHT 里的旧 02-*、03-* 键全部删掉
lines = src.splitlines()
out = []
for ln in lines:
    if re.match(r'^\s*"0[23]-s\d\d"', ln):
        continue
    out.append(ln)
src = "\n".join(out) + "\n"

# 2) 末尾加三集模块的覆盖
tail = '''
# 第02、03集（短剧版 18 拍）的映射同样由各自模块提供
import ep02_shots as E02
import ep03_shots as E03
for _k, _v in E02.REF.items():
    R["02-" + _k] = _v
for _k, _v in E02.COMP.items():
    COMP["02-" + _k] = _v
for _k, _v in E02.LIGHT.items():
    LIGHT["02-" + _k] = _v
for _k, _v in E03.REF.items():
    R["03-" + _k] = _v
for _k, _v in E03.COMP.items():
    COMP["03-" + _k] = _v
for _k, _v in E03.LIGHT.items():
    LIGHT["03-" + _k] = _v
'''
src = src.replace('STYLE_TAIL = "电影感写实', tail.strip() + '\n\nSTYLE_TAIL = "电影感写实')
open(p, "w", encoding="utf-8").write(src)
print("shots_flux patched")
