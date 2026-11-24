"""Reproduce CPS learner resources with existing aligned PDF/Artifact Tool builders."""
import argparse
import os
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
RELEASE='production_courseware/phase_eleven/cps_media_01'
PACKAGE='production_courseware/phase_eleven/cps_batch_01/review_package.json'
INTRO='Reference IDs identify appraised sources below. Cases and exercises are original fictional teaching. Child safeguarding and humanitarian standards are practice comparators, not Nigerian law, accreditation or deployment authority. Verify local procedures with authorised qualified practitioners. Publication, fieldwork and search dates differ. No source tools or protected exercises are reproduced.'
def main():
    p=argparse.ArgumentParser();p.add_argument('--font-regular',required=True);p.add_argument('--font-bold',required=True);p.add_argument('--node',required=True);p.add_argument('--node-modules',required=True);p.add_argument('--presentation-skill',required=True);p.add_argument('--runtime-python',required=True);p.add_argument('--soffice',required=True);p.add_argument('--pdftoppm',required=True)
    a=p.parse_args()
    if any((ROOT/RELEASE/'pptx').glob('*.pptx')) or any((ROOT/RELEASE/'.deck-build').glob('*-validation.json')):
        p.error('Archive existing CPS output before rebuilding; final decks and validation receipts are immutable.')
    env=dict(os.environ,CODEX_PRESENTATIONS_SKILL_DIR=a.presentation_skill,CODEX_RUNTIME_NODE_MODULES=a.node_modules,CODEX_RUNTIME_PYTHON=a.runtime_python,SWEEP_MATERIAL_RELEASE='approved')
    def run(args):subprocess.run(args,cwd=ROOT,env=env,check=True)
    run([sys.executable,'scripts/build_fsw_media_pdfs.py','--release',RELEASE,'--package',PACKAGE,'--font-regular',a.font_regular,'--font-bold',a.font_bold,'--reference-intro',INTRO,'--approved-materials'])
    run([a.node,'scripts/build_fsw_media_decks.mjs',RELEASE,'',PACKAGE])
    run([sys.executable,'scripts/render_fsw_media.py','--release',RELEASE,'--soffice',a.soffice,'--pdftoppm',a.pdftoppm])
    run([sys.executable,'scripts/build_fsw_media_manifest.py','--release',RELEASE,'--package',PACKAGE,'--approved-materials'])
    run([sys.executable,'scripts/build_courseware_contact_sheets.py','--release',RELEASE])
if __name__=='__main__':main()
