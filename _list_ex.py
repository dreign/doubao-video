import json
d = json.load(open(r"D:\AAA\text\假钦差\短剧\06_素材\workflows_scan.json", encoding="utf-8"))
print("== 节点包示例 ==")
for x in d["pack_examples"]:
    tag = "H3" if x.get("has_h3") else "  "
    print("[%s] %-44s %-52s nodes=%s" % (tag, x["dir"][:44], x["file"][:52], x.get("node_count")))
