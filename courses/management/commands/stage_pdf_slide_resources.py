"""Upload verified PDF/slide resources, then register a complete review batch."""
import hashlib
import json
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.parse import quote

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from courses.authored_review import digest
from courses.content_storage import SupabaseStorageClient, build_storage_path, canonical_storage_url, validate_upload_metadata
from courses.content_workflow import create_external_asset, transition_asset
from courses.curriculum_validation import validate_manifest
from courses.management.commands.stage_authored_review import snapshot
from courses.management.commands.upload_production_courseware import upload_bytes
from courses.models import Course
from schools.models import School


def verify_bytes(client, storage_path, checksum):
    # Signed URLs stay in memory and are never placed in receipts or logs.
    with urlopen(client.create_signed_download_url(storage_path), timeout=45) as response:
        if hashlib.sha256(response.read()).hexdigest() != checksum:
            raise CommandError("Remote resource checksum mismatch; no publication permitted")


def ensure_private_bucket(client):
    request=Request(f"{client.storage_api_url}/bucket/{quote(client.bucket,safe='')}",
        headers={"Authorization":f"Bearer {client.key}","apikey":client.key})
    with urlopen(request,timeout=30) as response:
        metadata=json.loads(response.read())
    if metadata.get("public") is not False:
        raise CommandError("Draft resources require a verified private Storage bucket")


class Command(BaseCommand):
    help="Validate or upload a complete PDF-and-slides batch to private Storage, entering review only."

    def add_arguments(self,parser):
        parser.add_argument("--release",type=Path,required=True)
        parser.add_argument("--manifest",type=Path,required=True)
        parser.add_argument("--commit",action="store_true")
        parser.add_argument("--receipt",type=Path)
        parser.add_argument("--verify",type=Path,help="Read-only check of a completed staging receipt")

    def preflight(self,manifest,*,allow_assets=False,lock=False):
        qs=Course.objects.select_for_update() if lock else Course.objects
        result={}
        for entry in manifest:
            try:
                course=qs.get(course_code=entry["course_code"],slug=entry["course_slug"])
            except Course.DoesNotExist as exc:
                raise CommandError("A resource points to a missing or mismatched course") from exc
            if course.is_active or not course.school.code or course.school.enrollment_open or course.paralearn_assessment_id:
                raise CommandError("This create-only review operation requires inactive coded-school drafts without an active CBT mapping")
            if course.enrollments.exists():
                raise CommandError("Draft course has learner enrolments; review the course state")
            if not allow_assets and course.assets.exists():
                raise CommandError("Course already has assets; this command cannot overwrite or silently skip them")
            result[entry["course_code"]]=course
        return result

    def handle(self,*args,**options):
        release=options["release"].resolve()
        manifest=json.loads(options["manifest"].read_text(encoding="utf-8"))
        validate_manifest(manifest,release=release,profile="pdf_slides")
        for entry in manifest:
            validate_upload_metadata(asset_type=entry["asset_type"],filename=Path(entry["path"]).name,
                content_type=entry["content_type"],size_bytes=entry["size_bytes"])
        if options["verify"]:
            if options["commit"]:
                raise CommandError("Choose verification or commit")
            return self.verify(manifest,options["verify"])
        self.preflight(manifest)
        if not options["commit"]:
            self.stdout.write(f"Validated {len(manifest)} PDF/slide files and inactive course identities; nothing uploaded or changed.")
            return
        receipt=options["receipt"]
        if not receipt:
            raise CommandError("--commit requires a new private --receipt path")
        applied=receipt.with_suffix(".applied.json")
        if applied.exists():
            raise CommandError("Applied receipt already exists")
        receipt.parent.mkdir(parents=True,exist_ok=True)
        client=SupabaseStorageClient()
        ensure_private_bucket(client)
        with receipt.open("x",encoding="utf-8") as handle:
            json.dump(dict(status="reserved",manifest_sha256=digest(manifest)),handle)
        uploaded=[]
        for entry in manifest:
            source=release/entry["path"]
            storage_path=build_storage_path(course_slug=entry["course_slug"],module_order=None,filename=source.name)
            signed=client.create_signed_upload_url(storage_path)
            upload_bytes(signed_url=signed.url,source=source,content_type=entry["content_type"])
            # Journal each object immediately, so any interrupted batch is traceable.
            item=dict(entry,storage_path=storage_path)
            with receipt.with_suffix(".uploads.jsonl").open("a",encoding="utf-8") as handle:
                handle.write(json.dumps(item)+"\n")
            verify_bytes(client,storage_path,entry["sha256"])
            uploaded.append(item)
        # Network operations are complete before taking database locks.
        with transaction.atomic():
            list(School.objects.select_for_update().filter(code__in=Course.objects.filter(course_code__in={e["course_code"] for e in manifest}).values_list("school__code",flat=True)))
            courses=self.preflight(manifest,lock=True)
            before=snapshot()
            ids=[]
            for order,entry in enumerate(uploaded):
                asset=create_external_asset(user=None,course=courses[entry["course_code"]],module=None,payload=dict(
                    title=entry["title"],asset_type=entry["asset_type"],version=entry["version"],language="en",
                    external_url=canonical_storage_url(entry["storage_path"]),storage_path=entry["storage_path"],
                    original_filename=Path(entry["path"]).name,content_type=entry["content_type"],size_bytes=entry["size_bytes"],
                    order=order,is_downloadable=True))
                transition_asset(user=None,asset=asset,action="submit")
                ids.append(asset.pk)
            after=snapshot({"courses.courseasset":ids})
            if before != after:
                raise CommandError("Existing record parity failed; all new metadata rolled back")
        payload=dict(status="in_review",timestamp=timezone.now().isoformat(),new_asset_ids=ids,manifest_sha256=digest(manifest),
            objects=uploaded,before=before,after=after)
        with applied.open("x",encoding="utf-8") as handle:
            json.dump(payload,handle,indent=2)
        self.stdout.write(f"Uploaded, downloaded and hash-verified {len(ids)} private resources; all registered in review. Existing records unchanged.")

    def verify(self,manifest,path):
        from courses.models import CourseAsset
        receipt=json.loads(path.read_text(encoding="utf-8"))
        if digest(manifest) != receipt["manifest_sha256"]:
            raise CommandError("Manifest changed after staging")
        courses=self.preflight(manifest,allow_assets=True)
        client=SupabaseStorageClient()
        ensure_private_bucket(client)
        if snapshot({"courses.courseasset":receipt["new_asset_ids"]}) != receipt["before"]:
            raise CommandError("Pre-existing records changed since the receipt; inspect without overwriting")
        for pk,entry in zip(receipt["new_asset_ids"],receipt["objects"],strict=True):
            asset=CourseAsset.objects.get(pk=pk)
            if (asset.course_id,asset.status,asset.storage_path,asset.size_bytes,asset.original_filename,asset.version,asset.content_type)!=(
                courses[entry["course_code"]].pk,"in_review",entry["storage_path"],entry["size_bytes"],Path(entry["path"]).name,entry["version"],entry["content_type"]):
                raise CommandError("Staged resource metadata drift")
            verify_bytes(client,asset.storage_path,entry["sha256"])
        self.stdout.write(f"Verified {len(receipt['new_asset_ids'])} private in-review resources and unchanged pre-existing records.")
