import os, sys
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
name = "场景_乱葬岗.png"
p = ("9:16 竖构图场景参考图，中国古代明代城外荒坡上的乱葬岗：齐腰高的枯黄荒草，露出大片黄褐色干土，"
     "坡地上有几处浅浅的土坑，坑边压着破草席与烂麻布，散落零星的碎石、断木桩和几根白骨，"
     "两株枯死黑树向上伸出画面，远处起伏黄土岗，灰白阴天薄雾，无人物，无建筑，"
     "画面中没有任何排列整齐的石碑、石板或墓园结构，也没有现代混凝土，质朴荒凉，写实历史剧质感")
r = P.gen_image(p, size="768x1344", ratio="9:16")
P.copy_out(r["data"][0]["path"], os.path.join(REF, name))
print("ok", os.path.getsize(os.path.join(REF, name)))
