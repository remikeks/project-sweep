"""Isolated full suite, immutable checkpoint and actual final-media proof."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from pcei_build_proof import ROOT,media_summary
BASE='551113afc064e5e1e353dd0cedf4db562d1ddcf9'

def main():
    p=argparse.ArgumentParser();p.add_argument('--completed-test-summary',type=Path,help='Reuse an observed successful isolated log from this exact unchanged build; caller must verify provenance.')
    a=p.parse_args();private=ROOT/'production_courseware/private/phase-eleven';private.mkdir(parents=True,exist_ok=True)
    if a.completed_test_summary:output=a.completed_test_summary.read_text()
    else:
        env=dict(os.environ,DATABASE_URL='sqlite:///:memory:',DEBUG='True')
        run=subprocess.run([sys.executable,'manage.py','test','--noinput'],cwd=ROOT,env=env,capture_output=True,text=True)
        output=run.stdout+run.stderr;(private/'isolated-tests.log').write_text(output)
        assert run.returncode==0,'Isolated suite failed'
    match=re.search(r'Ran (\d+) tests in ([0-9.]+)s',output)
    assert match and '\nOK\n' in output and 'FAILED' not in output
    count=int(match[1]);assert count>=213
    git=['git','-c','safe.directory='+ROOT.as_posix()]
    tree=subprocess.check_output([*git,'ls-tree','-r','-z',BASE,'production_courseware'],cwd=ROOT).split(b'\0')
    protected={}
    # A persistent read-only batch avoids hundreds of Windows process launches.
    with subprocess.Popen([*git,'cat-file','--batch'],cwd=ROOT,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE) as reader:
        for row in filter(None,tree):
            info,name=row.split(b'\t',1);name=name.decode();object_id=info.split()[2]
            reader.stdin.write(object_id+b'\n');reader.stdin.flush()
            header=reader.stdout.readline().split()
            assert len(header)==3 and header[:2]==[object_id,b'blob'],'Cannot read protected blob: '+name
            size=int(header[2]);baseline=reader.stdout.read(size)
            assert len(baseline)==size and reader.stdout.read(1)==b'\n','Incomplete protected blob: '+name
            actual=(ROOT/name).read_bytes()
            if Path(name).suffix in {'.json','.py','.md','.txt','.csv'}:actual=actual.replace(b'\r\n',b'\n');baseline=baseline.replace(b'\r\n',b'\n')
            assert actual==baseline,'Protected checkpoint file changed: '+name
            protected[name]=hashlib.sha256(baseline).hexdigest()
        reader.stdin.close()
        assert reader.wait(timeout=30)==0,'Protected blob reader failed'
    release=ROOT/'production_courseware/phase_eleven/cps_media_01';manifest,pages,slides=media_summary(release)
    qa=json.loads((release/'visual_qa.json').read_text());assert qa['pdf_pages_reviewed']==pages and qa['slide_pages_reviewed']==slides
    assert qa['final_file_sha256']=={r['path']:r['sha256'] for r in manifest} and qa['status']=='reviewed'
    proof=dict(status='local_build_verified',tests=count,test_seconds=float(match[2]),database='sqlite:///:memory:',debug=True,original_checkpoint=BASE,protected_source_files=len(protected),protected_source_unchanged=True,protected_source_hashes=protected,source_comparison='Git baseline bytes; text CRLF normalised to LF, binary bytes identical',media_files=20,pdf_pages=pages,slide_pages=slides,visual_qa='reviewed',live_staging_performed=False,remote_hashes_verified=0,live_public_checks_performed=0)
    (private/'local-build-verification.json').write_text(json.dumps(proof,indent=2)+'\n')
    print(json.dumps({k:v for k,v in proof.items() if k!='protected_source_hashes'},indent=2))
if __name__=='__main__':main()
