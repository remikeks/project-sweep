"""Verify the actual learner files and write the review upload manifest."""
import hashlib
import json
from pathlib import Path
import sys
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from pypdf import PdfReader

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from courses.authored_review import digest, validate_package
from courses.curriculum_validation import validate_manifest

release=ROOT/"production_courseware/phase_three/fsw_media_01"
package=json.loads((ROOT/"production_courseware/phase_two/fsw_batch_01/review_package.json").read_text(encoding="utf-8"))
validate_package(package)
manifest=[]
details=[]
ns={"a":"http://schemas.openxmlformats.org/drawingml/2006/main"}
for c in package["courses"]:
    prefix=f"{c['code']}-{c['slug']}"
    for kind,folder,suffix,label in [
        ("learner_guide","pdf","-learner-guide.pdf","Learner guide PDF"),
        ("worksheet","pdf","-practice-worksheet.pdf","Practice worksheet PDF"),
        ("slides","pptx","-course-slides.pptx","Editable course slides PPTX"),
        ("slides","pdf","-course-slides.pdf","Course slides PDF")]:
        file=release/folder/(prefix+suffix)
        raw=file.read_bytes()
        pages=None
        if file.suffix==".pdf":
            reader=PdfReader(file)
            pages=len(reader.pages)
            body="\n".join(p.extract_text() or "" for p in reader.pages)
            assert all((p.extract_text() or "").strip() for p in reader.pages),"Empty PDF page"
            assert c["code"] in body
            assert len(body)>600,"PDF has insufficient accessible text"
            if "course-slides" in suffix: assert pages==16
            if "worksheet" in suffix: assert pages==3
            for m in c["modules"]:
                assert m["title"] in " ".join(body.split()),f"Missing module in {file.name}"
        else:
            with ZipFile(file) as archive:
                slides=[n for n in archive.namelist() if n.startswith("ppt/slides/slide") and n.endswith(".xml")]
                assert len(slides)==16
                body="\n".join(t.text or "" for name in slides for t in ET.fromstring(archive.read(name)).findall(".//a:t",ns))
                for module in c["assessment"]["modules"]:
                    for point in module["teaching_points"]:
                        assert point["text"] in body,"Missing teaching point in editable slides"
                assert "is_correct" not in body and '"correct":' not in body
        entry=dict(course_code=c["code"],course_slug=c["slug"],school_code="FSW",module_order="",
            title=c["title"]+" "+label,asset_type=kind,path=file.relative_to(release).as_posix(),
            content_type="application/pdf" if file.suffix==".pdf" else "application/vnd.openxmlformats-officedocument.presentationml.presentation",
            size_bytes=len(raw),sha256=hashlib.sha256(raw).hexdigest(),version="0.1.0",language="en",publication_status="in_review")
        manifest.append(entry)
        details.append(dict(path=entry["path"],pages=pages,sha256=entry["sha256"]))
summary=validate_manifest(manifest,release=release,profile="pdf_slides")
(release/"upload_manifest.json").write_text(json.dumps(manifest,indent=2)+"\n",encoding="utf-8")
(release/"package_validation.json").write_text(json.dumps(dict(profile="pdf_slides",source_package_sha256=digest(package),
    summary=summary,files=details,video_status="not_produced",academic_review="pending"),indent=2)+"\n",encoding="utf-8")
print("Verified",summary,"with 32 editable slides, accessible PDF text and all teaching points.")
