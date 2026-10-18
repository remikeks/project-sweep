"""Activate only the checksum-verified four-course expansion after real CBT checks."""
import hashlib
import json
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from courses.content_storage import SupabaseStorageClient
from courses.curriculum_validation import validate_manifest
from courses.management.commands.revise_staged_expansion import (
    ASSET_FIELDS, MODULE_FIELDS, CODES, snapshot, save_journal, verify_remote,
)
from courses.models import Course, CourseAsset, CourseModule
from learning.models import CourseAssessmentAttempt, ParaLearnWebhookEvent
from learning.paralearn import ParaLearnClient


def current_state(*, lock=False):
    queries = [Course.objects.filter(course_code__in=CODES),
               CourseAsset.objects.filter(course__course_code__in=CODES),
               CourseModule.objects.filter(course__course_code__in=CODES)]
    if lock:
        queries = [query.select_for_update() for query in queries]
    courses, assets, modules = [query.order_by('pk') for query in queries]
    return {'courses': list(courses.values('id', 'course_code', 'slug', 'title', 'is_active', 'paralearn_assessment_id', 'passing_score')),
            'assets': list(assets.values(*ASSET_FIELDS)), 'modules': list(modules.values(*MODULE_FIELDS))}


def publish_atomically(before):
    """Network validation is complete before this short, all-or-nothing update."""
    with transaction.atomic():
        if current_state(lock=True) != before:
            raise CommandError('Expansion rows changed during verification; nothing published.')
        now = timezone.now()
        CourseAsset.objects.filter(pk__in=[a['id'] for a in before['assets']]).update(
            status='published', reviewed_at=now, published_at=now, updated_at=now)
        Course.objects.filter(pk__in=[c['id'] for c in before['courses']]).update(is_active=True)
        return current_state()


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--release', type=Path, required=True)
        parser.add_argument('--revision-journal', type=Path, required=True)
        parser.add_argument('--journal', type=Path, required=True)
        parser.add_argument('--qa-user', required=True)
        parser.add_argument('--commit', action='store_true')

    def handle(self, *args, **options):
        release = options['release'].resolve()
        manifest_bytes = (release / 'upload_manifest.json').read_bytes()
        identity = hashlib.sha256(manifest_bytes).hexdigest()
        before = current_state()
        journal_path = options['journal'].resolve()
        if journal_path.exists():
            saved = json.loads(journal_path.read_text())
            if saved['manifest_sha256'] != identity:
                raise CommandError('Publication journal belongs to another release.')
            if saved.get('committed'):
                if saved['after'] != before:
                    raise CommandError('Published rows changed; review instead of rerunning publication.')
                self.stdout.write('Already published; unchanged. No new rows or uploads.')
                return
            if saved['before'] != before:
                raise CommandError('Rows differ from the publication preflight journal.')
        manifest = json.loads(manifest_bytes)
        catalogue = json.loads((release / 'course_catalogue.json').read_text())
        validate_manifest(manifest, catalogue=catalogue, release=release, expected_school_count=2)
        staged = snapshot(manifest)
        revision = json.loads(options['revision_journal'].read_text())
        if not revision.get('committed') or staged != revision['after']:
            raise CommandError('Production must exactly match the committed staged revision.')
        visual = json.loads((release / 'evidence_receipt.json').read_text())
        if not (visual.get('owner_authorized') and visual.get('visual_review_complete') and visual.get('manifest_sha256') == identity):
            raise CommandError('Matching owner authorization and visual review are required.')
        review_dir = Path(settings.BASE_DIR) / 'production_courseware/expansion_review'
        for name, key in [('teaching_source.json', 'teaching_source_sha256'), ('assessment_source.json', 'assessment_source_sha256')]:
            if hashlib.sha256((review_dir / name).read_bytes()).hexdigest() != visual[key]:
                raise CommandError('Reviewed source changed.')
        if len({c['paralearn_assessment_id'] for c in before['courses']}) != 4:
            raise CommandError('Four distinct provider exam IDs are required.')
        client = ParaLearnClient()
        checks = []
        for course in before['courses']:
            exam_id = course['paralearn_assessment_id']
            if not exam_id.startswith('exam_') or Course.objects.filter(paralearn_assessment_id=exam_id).count() != 1:
                raise CommandError('Assessment identity missing or reused.')
            exam = client._request_json('GET', '/exams/' + exam_id)
            bank = json.loads((review_dir / f"{course['course_code'].lower()}-assessment-review.json").read_text())
            if not (exam['accessCode'] == course['course_code'] and exam['workspaceId'] == 'ws_sweep_prod'
                    and exam['isPublished'] is True and exam['accessType'] == 'ROSTER_ONLY'
                    and exam['durationMins'] == 60 and exam['totalMarks'] == 15 and exam['totalQuestions'] == 15
                    and exam['shuffleQuestions'] is True and exam['shuffleChoices'] is True and exam['showResultAfter'] is True
                    and course['passing_score'] == bank['proposed_pass_percent']):
                raise CommandError('Provider settings do not match the approved course assessment.')
            actual = [q['question'] for q in sorted(exam['questions'], key=lambda q: q['orderIndex'])]
            if len(actual) != len(bank['questions']) or len(actual) != 15:
                raise CommandError('Provider question count differs.')
            for got, want in zip(actual, bank['questions']):
                if (got['prompt'], got['type'], got['marks'], got.get('explanation'), got.get('section')) != (
                        want['question'], want['type'], want['marks'], want['rationale'], f"Module {want['module_order']}"):
                    raise CommandError('Provider question differs from the reviewed bank.')
                if [(o['text'], bool(o.get('isCorrect'))) for o in got['options']] != [(o['text'], o['correct']) for o in want['options']]:
                    raise CommandError('Provider answer key differs.')
            attempt = CourseAssessmentAttempt.objects.filter(
                user__username=options['qa_user'], course_id=course['id'],
                result_verified_at__isnull=False, provider_candidate_id__isnull=False,
                status__in=['failed', 'passed']).order_by('-result_verified_at').first()
            event = ParaLearnWebhookEvent.objects.filter(attempt=attempt, processing_error='', processed_at__isnull=False).first() if attempt else None
            if not event or event.payload.get('examId') != exam_id or event.payload.get('attemptId') != attempt.provider_attempt_id:
                raise CommandError('A real processed, signed QA result is required for each course.')
            checks.append({'course_code':course['course_code'], 'exam_id':exam_id,
                           'qa_attempt_id':str(attempt.pk), 'provider_attempt_id':attempt.provider_attempt_id,
                           'event_id':event.event_id, 'questions_verified':15,
                           'result_verified_at':attempt.result_verified_at.isoformat()})
            self.stdout.write(course['course_code'] + ': provider bank, settings and signed result verified')
        assets = {a['id']:a for a in before['assets']}
        storage = SupabaseStorageClient()
        def check_asset(entry):
            asset = assets[entry['target_id']]
            if asset['version'] != entry['version'] or asset['size_bytes'] != entry['size_bytes']:
                raise CommandError('Asset version or size differs from release.')
            verify_remote(storage, asset['storage_path'], entry['sha256'])
        with ThreadPoolExecutor(max_workers=4) as pool:
            list(pool.map(check_asset, manifest))
        journal = {'manifest_sha256':identity, 'before':before, 'checks':checks,
                   'remote_checksums_verified':32, 'owner_authorized':True,
                   'independent_subject_matter_review':False, 'committed':False}
        if not options['commit']:
            self.stdout.write('Preflight passed: four real assessments/results and 32 remote checksums. Nothing published.')
            return
        save_journal(journal_path, journal)
        journal['after'] = publish_atomically(before)
        journal['committed'] = True
        journal['published_at'] = timezone.now().isoformat()
        save_journal(journal_path, journal)
        self.stdout.write('Published 32 existing resources and activated four existing courses atomically. No duplicate rows or learner changes.')
