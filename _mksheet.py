from PIL import Image, ImageDraw
import glob,os
for ep in ["第02集","第03集"]:
    fs=sorted(glob.glob(f"03_图片/{ep}/s*.png"))
    tw,th=240,420
    cols=6; rows=(len(fs)+cols-1)//cols
    sheet=Image.new("RGB",(cols*tw, rows*th),(20,20,20))
    d=ImageDraw.Draw(sheet)
    for i,f in enumerate(fs):
        im=Image.open(f).convert("RGB"); im.thumbnail((tw,th-18))
        x=(i%cols)*tw; y=(i//cols)*th
        sheet.paste(im,(x,y+18))
        d.text((x+6,y+2), os.path.basename(f).replace(".png",""), fill=(255,220,120))
    out=f"_qb_{ep}.jpg"
    sheet.save(out, quality=88)
    print(out, sheet.size, len(fs))
