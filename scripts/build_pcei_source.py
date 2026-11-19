"""Compile five additions against all seven retained review packages."""
from pathlib import Path
import subprocess
import sys
ROOT=Path(__file__).resolve().parents[1]
PRIOR=['phase_two/fsw_batch_01','phase_four/fsw_batch_02','phase_five/ert_batch_01','phase_six/ert_batch_02','phase_seven/gbv_batch_01','phase_eight/gbv_batch_02','phase_nine/mhp_batch_01']
def main():
    args=[sys.executable,str(ROOT/'scripts/build_course_review_batch.py'),'--authoring','production_courseware/phase_ten/pcei_batch_01/authoring.py','--output','production_courseware/phase_ten/pcei_batch_01']
    for p in PRIOR:args+=['--previous-package','production_courseware/'+p+'/review_package.json']
    subprocess.run(args,cwd=ROOT,check=True)
    subprocess.run([sys.executable,'scripts/build_pcei_eight_course_exam.py'],cwd=ROOT,check=True)
if __name__=='__main__':main()
