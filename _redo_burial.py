import os, sys, shutil
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
OLD = r"D:\AAA\text\假钦差\短剧\06_素材\旧_文生图版"
os.makedirs(OLD, exist_ok=True)
name = "场景_乱葬岗.png"
cur = os.path.join(REF, name)
if os.path.exists(cur):
    shutil.copy2(cur, os.path.join(OLD, "场景_乱葬岗_旧_现代墓碑版.png"))
p = ("9:16 竖构图场景参考图，中国古代明代县城外的乱葬岗荒坡：齐腰枯黄荒草、裸露的黄土与浅土坑，"
     "几块歪斜残破的青灰石碑与无字残碑散在草丛里，石碑残缺、字迹磨平，绝不成行排列；"
     "两株枯死黑树向上伸出画面，远处起伏黄土坡，灰白阴天薄雾，无人物，无建筑，"
     "严禁现代水泥墓碑、严禁整齐墓园、严禁平整的抛光石板、严禁电线与车辆，写实历史剧质感")
r = P.gen_image(p, size="768x1344", ratio="9:16")
P.copy_out(r["data"][0]["path"], cur)
print("ok", os.path.getsize(cur))
