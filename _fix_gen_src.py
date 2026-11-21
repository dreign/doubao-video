import importlib.util as u
import sys
p = r"D:\AAA\text\假钦差\短剧\_mk_ep01_v2.py"
s = open(p, encoding="utf-8").read()
old = "import ep01_shots as E"
new = ('_spec = u.spec_from_file_location("ep01_v1", r"%s")\n'
       'E = u.module_from_spec(_spec); _spec.loader.exec_module(E)' % r"D:\AAA\text\假钦差\短剧\06_素材\ep01_shots_v1_备份.py")
assert s.count(old) == 1
s = s.replace(old, new)
open(p, "w", encoding="utf-8").write(s)
print("generator now reads v1 backup")
