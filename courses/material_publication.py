"""Owner-authorised teaching-material release, separate from assessment readiness."""
from pathlib import Path
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from urllib.request import urlopen

from django.apps import apps
from django.core.management.base import CommandError
from django.db import transaction
from django.utils import timezone

from .authored_review import course_values, digest, lesson_text, validate_package
from .content_storage import SupabaseStorageClient, canonical_storage_url
from .curriculum_validation import validate_manifest
from .management.commands.stage_pdf_slide_resources import ensure_private_bucket
from .models import Course, CourseAsset
from schools.models import School


RELEASES = [
    ('phase_two/fsw_batch_01', 'phase_three/fsw_media_01'),
    ('phase_four/fsw_batch_02', 'phase_four/fsw_media_02'),
    ('phase_five/ert_batch_01', 'phase_five/ert_media_01'),
    ('phase_six/ert_batch_02', 'phase_six/ert_media_02'),
    ('phase_seven/gbv_batch_01', 'phase_seven/gbv_media_01'),
    ('phase_eight/gbv_batch_02', 'phase_eight/gbv_media_02'),
    ('phase_nine/mhp_batch_01', 'phase_nine/mhp_media_01'),
    ('phase_ten/pcei_batch_01', 'phase_ten/pcei_media_01'),
]
COURSE_FIELDS = {'is_active', 'updated_at'}
ASSET_FIELDS = {'status', 'reviewed_at', 'published_at', 'updated_at'}
RELEASE_PLANS = {
    '2026-11-19': dict(batches=RELEASES, codes=range(35, 66), scope='SWP-035-SWP-065 materials and individual course access'),
    'cps-2026-11-24': dict(batches=[('phase_eleven/cps_batch_01', 'phase_eleven/cps_media_01')], codes=range(66, 71), scope='SWP-066-SWP-070 materials and individual course access'),
    'spg-2026-11-25': dict(batches=[('phase_twelve/spg_batch_01', 'phase_twelve/spg_media_01')], codes=range(71, 78), scope='SWP-071-SWP-077 materials and individual course access'),
    'see-2026-11-27': dict(batches=[('phase_thirteen/see_batch_01', 'phase_thirteen/see_media_01')], codes=range(78, 84), scope='SWP-078-SWP-083 materials and individual course access'),
    'dai-2026-11-27': dict(batches=[('phase_fourteen/dai_batch_01', 'phase_fourteen/dai_media_01')], codes=range(84, 91), scope='SWP-084-SWP-090 materials and individual course access'),
    'blu-2026-11-27': dict(batches=[('phase_fifteen/blu_batch_01', 'phase_fifteen/blu_media_01')], codes=range(91, 97), scope='SWP-091-SWP-096 materials and individual course access'),
    'eil-2026-11-28': dict(batches=[('phase_sixteen/eil_batch_01', 'phase_sixteen/eil_media_01')], codes=range(97, 105), scope='SWP-097-SWP-104 materials and individual course access'),
}


def load_entries(root, release='2026-11-19'):
    if release not in RELEASE_PLANS:
        raise CommandError('Unknown owner material release')
    plan = RELEASE_PLANS[release]
    entries = []
    for batch, media in plan['batches']:
        package = json.loads((root/batch/'review_package.json').read_text(encoding='utf-8'))
        validate_package(package)
        release = root/media
        manifest = json.loads((release/'upload_manifest.json').read_text(encoding='utf-8'))
        validate_manifest(manifest, release=release, profile='pdf_slides')
        for course in package['courses']:
            rows = [r for r in manifest if r['course_code'] == course['code']]
            if len(rows) != 4:
                raise CommandError('Expected four designed resources per course')
            entries.append(dict(course=course, references=package['references'], assets=rows))
    if len(entries) != len(plan['codes']) or {e['course']['code'] for e in entries} != {f'SWP-{n:03}' for n in plan['codes']}:
        raise CommandError('Course scope differs from the selected owner release')
    return entries


def protected_snapshot(course_ids, asset_ids):
    """Protect all rows, excluding only authorised lifecycle columns on targets."""
    result = {}
    for label in ('schools', 'courses', 'learning', 'credentials'):
        for model in apps.get_app_config(label).get_models():
            rows = list(model.objects.order_by('pk').values())
            for row in rows:
                omitted = set()
                if model is Course and row['id'] in course_ids:
                    omitted = COURSE_FIELDS
                elif model is CourseAsset and row['id'] in asset_ids:
                    omitted = ASSET_FIELDS
                for field in omitted:
                    row.pop(field, None)
            result[model._meta.label_lower] = dict(count=len(rows), sha256=digest(json.loads(json.dumps(rows, default=str))))
    return result


def lifecycle_state(course_ids, asset_ids, *, lock=False):
    courses = Course.objects.filter(pk__in=course_ids).order_by('pk')
    assets = CourseAsset.objects.filter(pk__in=asset_ids).order_by('pk')
    if lock:
        courses = courses.select_for_update()
        assets = assets.select_for_update()
    # Querysets are evaluated here so lock acquisition is deterministic.
    return dict(courses=list(courses.values('id', *sorted(COURSE_FIELDS))),
                assets=list(assets.values('id', *sorted(ASSET_FIELDS))))


def preflight(entries):
    codes = [e['course']['code'] for e in entries]
    courses = list(Course.objects.filter(course_code__in=codes).select_related('school').prefetch_related('modules', 'assets'))
    by_code = {c.course_code: c for c in courses}
    if len(courses) != len(entries) or len(by_code) != len(entries):
        raise CommandError('Missing or duplicate release course identity')
    resources = []
    for entry in entries:
        source = entry['course']
        course = by_code[source['code']]
        if course.school.code != source['school_code'] or course.school.enrollment_open or course.school.is_historical:
            raise CommandError('School readiness state changed')
        if course.paralearn_assessment_id or course.is_active:
            raise CommandError('Expected inactive material-only additions with unchanged blank CBT IDs')
        for field, value in course_values(source, entry['references']).items():
            if getattr(course, field) != value:
                raise CommandError(f'{course.course_code}: source course drift in {field}')
        modules = sorted(course.modules.all(), key=lambda m: m.order)
        if len(modules) != 3:
            raise CommandError('Expected three retained authored modules')
        for module, expected in zip(modules, source['modules'], strict=True):
            if (module.order, module.title, module.overview, module.content, module.practical_activity) != (
                    expected['order'], expected['title'], expected['outcome'], lesson_text(expected, entry['references']), expected['activity']):
                raise CommandError('Source module drift; no publication permitted')
        assets = list(course.assets.all())
        if len(assets) != 4:
            raise CommandError('Resource count changed')
        by_name = {a.original_filename: a for a in assets}
        if len(by_name) != 4:
            raise CommandError('Duplicate resource identity')
        for row in entry['assets']:
            asset = by_name.get(Path(row['path']).name)
            if asset is None or asset.status != 'in_review' or asset.module_id or asset.replaces_id or asset.file:
                raise CommandError('Only unchanged in-review course-wide resources may be released')
            expected = (row['title'], row['asset_type'], row['version'], row['language'], row['content_type'], row['size_bytes'])
            actual = (asset.title, asset.asset_type, asset.version, asset.language, asset.content_type, asset.size_bytes)
            if actual != expected or not asset.is_downloadable or not asset.storage_path:
                raise CommandError('Resource metadata drift')
            if asset.external_url != canonical_storage_url(asset.storage_path):
                raise CommandError('Resource is not the expected private storage object')
            resources.append(dict(asset_id=asset.pk, course_code=course.course_code,
                                  storage_path=asset.storage_path, path=row['path'], sha256=row['sha256']))
    course_ids = {c.pk for c in courses}
    asset_ids = {r['asset_id'] for r in resources}
    return course_ids, asset_ids, resources


def verify_remote_resources(resources):
    client = SupabaseStorageClient()
    ensure_private_bucket(client)

    def verify(row):
        with urlopen(client.create_signed_download_url(row['storage_path']), timeout=45) as response:
            actual = hashlib.sha256(response.read()).hexdigest()
        if actual != row['sha256']:
            raise CommandError('Remote material checksum mismatch')
        return dict(asset_id=row['asset_id'], sha256=actual)

    with ThreadPoolExecutor(max_workers=6) as pool:
        verified = list(pool.map(verify, resources))
    return verified


@transaction.atomic
def publish_atomically(course_ids, asset_ids, before, protected):
    school_ids = Course.objects.filter(pk__in=course_ids).values_list('school_id', flat=True).distinct()
    list(School.objects.filter(pk__in=school_ids).order_by('pk').select_for_update())
    if lifecycle_state(course_ids, asset_ids, lock=True) != before:
        raise CommandError('Lifecycle changed during verification; nothing published')
    if protected_snapshot(course_ids, asset_ids) != protected:
        raise CommandError('Protected records changed during verification; nothing published')
    now = timezone.now()
    approved = CourseAsset.objects.filter(pk__in=asset_ids, status='in_review').update(
        status='approved', reviewed_at=now, updated_at=now)
    if approved != len(asset_ids):
        raise CommandError('Approval scope changed')
    published = CourseAsset.objects.filter(pk__in=asset_ids, status='approved').update(
        status='published', published_at=now, updated_at=now)
    activated = Course.objects.filter(pk__in=course_ids, is_active=False).update(is_active=True, updated_at=now)
    if published != len(asset_ids) or activated != len(course_ids):
        raise CommandError('Publication scope changed')
    if protected_snapshot(course_ids, asset_ids) != protected:
        raise CommandError('Protected record parity failed; publication rolled back')
    return lifecycle_state(course_ids, asset_ids)
