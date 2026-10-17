"""Invoke the packaged DOCX renderer with an explicitly approved isolated engine.

The Windows artifact runtime resets inherited PATH. Set the approved paths
inside Python, without changing the system environment or the packaged tool.
"""
import argparse
import os
import runpy
import sys
from pathlib import Path

parser = argparse.ArgumentParser()
parser.add_argument("--renderer", type=Path, required=True)
parser.add_argument("--libreoffice-dir", type=Path, required=True)
parser.add_argument("--poppler-dir", type=Path, required=True)
args, renderer_args = parser.parse_known_args()
for required in (args.renderer, args.libreoffice_dir / "soffice.exe", args.poppler_dir / "pdftoppm.exe"):
    if not required.is_file():
        raise FileNotFoundError(required)
os.environ["PATH"] = os.pathsep.join((str(args.libreoffice_dir.resolve()), str(args.poppler_dir.resolve()), os.environ.get("PATH", "")))
sys.argv = [str(args.renderer), *renderer_args]
runpy.run_path(str(args.renderer), run_name="__main__")
