"""Build labelled visual-QA contact sheets from already-rendered final PDFs."""
import argparse
from pathlib import Path
from PIL import Image,ImageDraw

parser=argparse.ArgumentParser()
parser.add_argument("--release",type=Path,required=True)
args=parser.parse_args()
out=args.release/"qa/contact-sheets"
out.mkdir(parents=True,exist_ok=True)
for folder in sorted((args.release/"qa/pdf").iterdir()):
    if not folder.is_dir():continue
    pages=sorted(folder.glob("page-*.png"),key=lambda p:int(p.stem.split("-")[-1]))
    width,height=(800,450) if "course-slides" in folder.name else (540,764)
    for start in range(0,len(pages),4):
        sheet=Image.new("RGB",(width*2,(height+28)*2),"#dfe4e8")
        draw=ImageDraw.Draw(sheet)
        for slot,page in enumerate(pages[start:start+4]):
            with Image.open(page) as original:
                original.thumbnail((width,height))
                x=(slot%2)*width+(width-original.width)//2
                y=(slot//2)*(height+28)+28
                sheet.paste(original,(x,y))
            draw.text(((slot%2)*width+10,(slot//2)*(height+28)+8),folder.name[:63]+" / "+page.stem,fill="#162a47")
        sheet.save(out/f"{folder.name}-{start//4+1:02}.jpg",quality=92)
print(out)
