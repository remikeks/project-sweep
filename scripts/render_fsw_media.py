"""Render final slides through isolated LibreOffice and all PDFs through Poppler."""
import argparse
from pathlib import Path
import subprocess
import tempfile

parser=argparse.ArgumentParser()
parser.add_argument("--release",type=Path,required=True)
parser.add_argument("--soffice",type=Path,required=True)
parser.add_argument("--pdftoppm",type=Path,required=True)
parser.add_argument("--code",default="")
parser.add_argument("--pdf-only",action="store_true")
args=parser.parse_args()
release=args.release.resolve()
for deck in ([] if args.pdf_only else sorted((release/"pptx").glob(args.code+"*.pptx"))):
    with tempfile.TemporaryDirectory(prefix="sweep-slide-render-") as temporary:
        profile=Path(temporary)/"profile"
        command=[str(args.soffice.resolve()),"-env:UserInstallation="+profile.as_uri(),"--headless","--convert-to","pdf:impress_pdf_Export",
                 "--outdir",str(release/"pdf"),str(deck)]
        result=subprocess.run(command,capture_output=True,text=True,timeout=120)
        if result.returncode or not (release/"pdf"/(deck.stem+".pdf")).is_file():
            raise RuntimeError("Slide PDF conversion failed: "+result.stdout+result.stderr)
        print(deck.name,"converted to matching slide PDF",flush=True)
for pdf in sorted((release/"pdf").glob(args.code+"*.pdf")):
    out=release/"qa"/"pdf"/pdf.stem
    out.mkdir(parents=True,exist_ok=True)
    if not out.resolve().is_relative_to(release):
        raise ValueError("QA output must remain within the release")
    for stale in out.glob("page-*.png"):
        if stale.is_file():
            stale.unlink()
    subprocess.run([str(args.pdftoppm.resolve()),"-r","100","-png",str(pdf),str(out/"page")],check=True,timeout=90,capture_output=True)
    print(pdf.name,"rendered for visual inspection",flush=True)
