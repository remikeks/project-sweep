"""Extract the release learner guides for ParaLearn's text-source input."""
import json
from pathlib import Path
import xml.etree.ElementTree as ET
import zipfile

ROOT = Path(__file__).resolve().parents[1]
RELEASE = ROOT / "production_courseware" / "release-2026-10-03"
courses = json.loads((RELEASE / "course_catalogue.json").read_text(encoding="utf-8"))
ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
for course in courses:
    source = RELEASE / "docx" / f"{course['number']:02d}-{course['slug']}-learner-guide.docx"
    with zipfile.ZipFile(source) as archive:
        doc = ET.fromstring(archive.read("word/document.xml"))
    course["source_text"] = "\n".join(
        "".join(p.itertext()) for p in doc.findall(".//w:p", ns)
    )
    course["source_file"] = str(source)
output = RELEASE / "paralearn_source_text.json"
output.write_text(json.dumps(courses, ensure_ascii=False, indent=2), encoding="utf-8")
print(f"Extracted {len(courses)} learner guides to {output}")
