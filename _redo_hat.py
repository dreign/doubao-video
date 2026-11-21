import os, sys
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
name = "物品_乌纱帽.png"
p = ("9:16 竖构图道具参考图，一顶中国古代明代乌纱帽正面平放特写：黑色圆顶帽身，贴合头部，"
     "左右两侧各一根细长平直帽翅向两边水平伸出，帽翅前端略窄，材质为黑纱与漆木，表面哑光，"
     "帽身有极细的织纹与旧磨痕，深灰背景，均匀柔光，无人物，写实历史剧质感，无文字")
r = P.gen_image(p, size="768x1344", ratio="9:16")
P.copy_out(r["data"][0]["path"], os.path.join(REF, name))
print("ok", os.path.getsize(os.path.join(REF, name)))
