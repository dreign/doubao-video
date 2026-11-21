import sys, os
sys.path.insert(0, r"D:\AAA\text\假钦差\短剧")
import pipeline as P
REF = r"D:\AAA\text\假钦差\短剧\06_素材\参考库"
name = "物品_通缉画像.png"
p = ("9:16 竖构图道具参考图，一张贴在木板上的陈旧通缉告示，泛黄粗纸，边缘破损，"
     "纸面正中画着一名蓄络腮胡的凶悍男子头像，五官粗野、额头有一道斜疤，墨线勾勒、笔触僵硬，"
     "四周有朱红官印痕迹与模糊墨字但文字不可辨认，木板与纸面有钉痕和撕裂，柔和冷灰光，正面平视，写实历史剧质感")
r = P.gen_image(p, size="768x1344", ratio="9:16")
P.copy_out(r["data"][0]["path"], os.path.join(REF, name))
print("ok", name, os.path.getsize(os.path.join(REF, name)))
