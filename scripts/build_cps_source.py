"""Compile CPS additions against every prior authored assessment bank."""
from pathlib import Path
import subprocess
import sys
ROOT = Path(__file__).resolve().parents[1]
PRIOR = ['phase_two/fsw_batch_01', 'phase_four/fsw_batch_02', 'phase_five/ert_batch_01', 'phase_six/ert_batch_02', 'phase_seven/gbv_batch_01', 'phase_eight/gbv_batch_02', 'phase_nine/mhp_batch_01', 'phase_ten/pcei_batch_01']


def main():
    args = [sys.executable, 'scripts/build_course_review_batch.py', '--authoring', 'production_courseware/phase_eleven/cps_batch_01/authoring.py', '--output', 'production_courseware/phase_eleven/cps_batch_01']
    for batch in PRIOR:
        args += ['--previous-package', f'production_courseware/{batch}/review_package.json']
    subprocess.run(args, cwd=ROOT, check=True)
    subprocess.run([sys.executable, 'scripts/build_cps_eight_course_exam.py'], cwd=ROOT, check=True)


if __name__ == '__main__':
    main()
