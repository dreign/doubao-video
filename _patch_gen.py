import io, re
p = r"D:\AAA\text\假钦差\短剧\_mk_ep01_v2.py"
s = open(p, encoding="utf-8").read()
old_block = '''    if key in DIA:
        new_line, new_sentence = DIA[key]
        if line:
            assert h3.count(line) == 1, f"{sid} 台词在 h3 中不是唯一：{line}"
            h3 = h3.replace(line, new_sentence)
        line = new_line'''
new_block = '''    if key in DIA:
        new_line, new_sentence = DIA[key]
        if line and h3.count(line) == 1:
            h3 = h3.replace(line, new_sentence)
        elif sid == "s01":
            anchor = "远处宣读声带回声"
            assert h3.count(anchor) == 1, "s01 宣读锚点不唯一"
            h3 = h3.replace(anchor, "远处宣读声带回声，画外宣读：“%s”" % new_sentence)
        line = new_line'''
assert old_block in s
s = s.replace(old_block, new_block)
open(p, "w", encoding="utf-8").write(s)
print("patched")
