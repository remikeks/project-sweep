"""PCEI evidence, curriculum/exam boundaries, real files and additive staging."""
import copy
import hashlib
import io
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from django.core.management import call_command
from django.test import SimpleTestCase, TestCase
from courses.test_ert_phase_five import read,module
from courses.authored_review import validate_package
from courses.assessment_review_validation import validate_review_bank
from courses.curriculum_validation import validate_manifest
from courses.models import Course,CourseModule,CourseAsset
from schools.models import School
from schools.exam_blueprints import validate_blueprint
from schools.pcei_exam_review import review_pcei_result
ROOT=Path(__file__).resolve().parents[1]
BATCH=ROOT/'production_courseware/phase_ten/pcei_batch_01'
MEDIA=ROOT/'production_courseware/phase_ten/pcei_media_01'
PRIOR=['phase_two/fsw_batch_01','phase_four/fsw_batch_02','phase_five/ert_batch_01','phase_six/ert_batch_02','phase_seven/gbv_batch_01','phase_eight/gbv_batch_02','phase_nine/mhp_batch_01']

class PceiSourceTests(SimpleTestCase):
    def test_determinism_word_depth_and_390_prior_stem_rejection(self):
        compiler=module(ROOT/'scripts/build_course_review_batch.py','pcei_compiler')
        source=module(BATCH/'authoring.py','pcei_source')
        data=read(BATCH/'review_package.json')
        self.assertEqual(compiler.compile_package(source),data)
        self.assertEqual(validate_package(data),dict(courses=5,modules=15,questions=75))
        prior=[q['question'] for p in PRIOR for c in read(ROOT/'production_courseware'/p/'review_package.json')['courses'] for q in c['assessment']['questions']]
        self.assertEqual(len(prior),390)
        for c in data['courses']:
            self.assertEqual(c['school_code'],'PCEI')
            self.assertIn('fictional',c['study_guidance']);self.assertIn('not completed field placement',c['study_guidance'])
            for m in c['modules']:self.assertGreaterEqual(len(' '.join(m['paragraphs']).split()),250)
            identity=dict(code=c['code'],title=c['title'],slug=c['slug'],modules=c['modules'])
            validate_review_bank(c['assessment'],identity,existing_stems=prior)
            duplicate=copy.deepcopy(c['assessment']);duplicate['questions'][0]['question']=prior[0]
            with self.assertRaises(ValueError):validate_review_bank(duplicate,identity,existing_stems=prior)
            prior.extend(q['question'] for q in c['assessment']['questions'])

    def test_evidence_dates_rights_overlap_and_bounded_claims(self):
        data=read(BATCH/'review_package.json');refs={r['id']:r for r in data['references']}
        self.assertEqual(data['evidence_checked_on'],'2026-11-16')
        self.assertEqual(refs['S31']['year'],2018)
        self.assertIn('not new editions',refs['S31']['appraisal'])
        for r in refs.values():
            self.assertEqual(r['checked_on'],'2026-11-16');self.assertTrue(r['licence']);self.assertTrue(r['use']);self.assertTrue(r['appraisal'])
        self.assertIn('2021',refs['R41']['appraisal']);self.assertIn('2019-20',refs['R43']['appraisal'])
        self.assertIn('2 January 2024',refs['R42']['appraisal'])
        self.assertIn('overlap unresolved',refs['R44']['appraisal']);self.assertIn('third n/header mismatch',refs['R44']['appraisal'])
        self.assertIn('No Q1/Q2',refs['R44']['quartile'])
        self.assertEqual(data['review']['safeguarding'],'pending')

    def test_eight_course_exam_actual_retained_domains_and_written_coverage(self):
        b=read(BATCH/'school_exam_blueprint.json');builder=module(ROOT/'scripts/build_pcei_eight_course_exam.py','pcei_exam')
        self.assertEqual(b,builder.blueprint())
        self.assertEqual(validate_blueprint(b),dict(courses=8,items=48,marks=100,unbound_mcqs=40,ready_for_launch=False))
        originals=[c for c in read(ROOT/'production_courseware/release-2026-10-03/course_catalogue.json') if c['code'] in b['required_courses'][:3]]
        self.assertEqual(b['retained_course_domains'],{c['code']:{k:c[k] for k in ['title','outcome','modules','cbt_focus']} for c in originals})
        for code in b['required_courses']:self.assertEqual(sum(i['type']=='MCQ' and i['course_codes']==[code] for i in b['items']),5)
        self.assertEqual({c for i in b['items'] if i['type']=='SHORT_ANSWER' for c in i['course_codes']},set(b['required_courses']))
        for i in b['items']:
            if i['type']=='ESSAY':self.assertEqual(i['course_codes'],b['required_courses'])
        self.assertFalse(b['curriculum_complete']);self.assertTrue(b['draft_catalogue_complete']);self.assertIsNone(b['provider_assessment_id'])

    def test_human_criterion_marking_independent_moderation_and_no_offline_certificate(self):
        b=read(BATCH/'school_exam_blueprint.json')
        result=dict(school_code='PCEI',curriculum_version=b['curriculum_version'],completed_courses=b['required_courses'],status='finalized',moderation_status='approved',item_results=[])
        for i in b['items']:
            result['item_results'].append(dict(id=i['id'],score=i['marks'],marking_status='marked',human_marker_id='fixture-marker',human_moderator_id='fixture-moderator',moderation_status='approved',rubric_version='draft-0.1.0',moderation_rationale='Fictional review checked against rubric.',amendment_history=[],appeal_history=[],criterion_results=[dict(criterion=r['criterion'],score=r['marks'],rationale='Fictional answer meets criterion with applied reasoning.') for r in i.get('rubric',[])]))
        good=review_pcei_result(b,result,verified_transport=True)
        self.assertTrue(good['contract_checks_passed']);self.assertFalse(good['certificate_authorised'])
        self.assertFalse(review_pcei_result(b,result)['contract_checks_passed'])
        cases=[('completed_courses',b['required_courses'][:-1]),('moderation_status','pending')]
        for field,value in cases:
            bad=copy.deepcopy(result);bad[field]=value
            self.assertFalse(review_pcei_result(b,bad,verified_transport=True)['contract_checks_passed'])
        for field,value in [('human_marker_id',''),('human_moderator_id','fixture-marker'),('criterion_results',[]),('amendment_history',None),('rubric_version','')]:
            bad=copy.deepcopy(result);bad['item_results'][40][field]=value
            self.assertFalse(review_pcei_result(b,bad,verified_transport=True)['contract_checks_passed'])
        for field,value in [('score',4),('rationale','')]:
            bad=copy.deepcopy(result);bad['item_results'][40]['criterion_results'][0][field]=value
            self.assertFalse(review_pcei_result(b,bad,verified_transport=True)['contract_checks_passed'])

    def test_completion_report_rejects_incomplete_or_mismatched_bridge_proof(self):
        proof=module(ROOT/'scripts/pcei_build_proof.py','pcei_proof')
        manifest=read(MEDIA/'upload_manifest.json')
        # Deliberately synthetic in-memory schema fixture, never saved as live proof.
        fixture=dict(school_code='PCEI',preexisting_parity=True,source_courses_verified=5,private_resources_verified=20,total_courses=65,active_courses=34,inactive_drafts=31,total_assets=396,school_courses=8,school_target=8,closed_coded_schools=25,remote_files=[dict(path=r['path'],sha256=r['sha256']) for r in manifest],public_checks=[dict(path=p,status=s,passed=True) for p,s in proof.expected_public_checks().items()],verification_provenance='Synthetic unit fixture only',verified_on='not-live-unit-fixture')
        self.assertTrue(proof.validate_live_proof(fixture,manifest))
        for field,value in [('preexisting_parity',False),('private_resources_verified',19),('total_assets',395),('remote_files',fixture['remote_files'][:-1]),('public_checks',fixture['public_checks'][:-1])]:
            bad=copy.deepcopy(fixture);bad[field]=value
            with self.assertRaises(AssertionError):proof.validate_live_proof(bad,manifest)
        bad=copy.deepcopy(fixture);bad['remote_files'][0]['sha256']='0'*64
        with self.assertRaises(AssertionError):proof.validate_live_proof(bad,manifest)
        bad=copy.deepcopy(fixture);bad['public_checks'][1]['status']=200
        with self.assertRaises(AssertionError):proof.validate_live_proof(bad,manifest)

    def test_actual_twenty_resources_and_all_seven_prior_media_manifests(self):
        manifest=read(MEDIA/'upload_manifest.json')
        self.assertEqual(validate_manifest(manifest,release=MEDIA,profile='pdf_slides'),dict(assets=20,asset_courses=5))
        self.assertEqual({r['school_code'] for r in manifest},{'PCEI'})
        self.assertTrue(all(r['publication_status']=='in_review' for r in manifest))
        for p in ['phase_three/fsw_media_01','phase_four/fsw_media_02','phase_five/ert_media_01','phase_six/ert_media_02','phase_seven/gbv_media_01','phase_eight/gbv_media_02','phase_nine/mhp_media_01']:
            release=ROOT/'production_courseware'/p
            validate_manifest(read(release/'upload_manifest.json'),release=release,profile='pdf_slides')
        from pypdf import PdfReader
        import pdfplumber
        for row in manifest:
            if row['asset_type'] not in {'learner_guide','worksheet'}:continue
            reader=PdfReader(MEDIA/row['path'])
            if row['asset_type']=='worksheet':self.assertEqual(len(reader.pages),3)
            for page in reader.pages:
                fonts=[f.get_object() for f in page['/Resources']['/Font'].values()]
                embedded=[f for f in fonts if f.get('/FontDescriptor') and f['/FontDescriptor'].get('/FontFile2')]
                self.assertGreaterEqual(len(embedded),2)
                text=' '.join(page.extract_text().split());self.assertIn('PCEI',text)
                if row['asset_type']=='worksheet':self.assertIn('Do not collect real complainant',text)
            if row['asset_type']=='learner_guide':
                with pdfplumber.open(MEDIA/row['path']) as pdf:
                    sizes=[round(ch['size'],1) for p in pdf.pages for ch in p.chars if ch.get('text','').isalpha()]
                self.assertGreater(sizes.count(12.0),500)

class PceiStagingTests(TestCase):
    def test_create_only_preserves_three_cbts_assets_drafts_learners_credentials_and_rejects_replay(self):
        from django.contrib.auth import get_user_model
        from django.core.management.base import CommandError
        from courses.management.commands.stage_authored_review import snapshot
        from learning.models import CourseEnrollment,CourseProgress
        from credentials.models import Badge,Certificate
        school=School.objects.create(name='PCEI',code='PCEI',target_course_count=8,enrollment_open=False)
        originals=[]
        for c in read(ROOT/'production_courseware/release-2026-10-03/course_catalogue.json'):
            if c['code'] not in ['SWP-013','SWP-014','SWP-015']:continue
            row=Course.objects.create(school=school,course_code=c['code'],title=c['title'],content='Protected original',paralearn_assessment_id='fixture-cbt-'+c['code'])
            for m in c['modules']:CourseModule.objects.create(course=row,order=m['order'],title=m['title'],content=m['focus'])
            CourseAsset.objects.create(course=row,title='Protected original resource',asset_type='learner_guide',storage_path='fixture-only/original.pdf',status='published')
            originals.append(row)
        oldschool=School.objects.create(name='MHP',code='MHP',enrollment_open=False)
        old=Course.objects.create(school=oldschool,course_code='SWP-057',title='Protected prior draft',is_active=False)
        CourseAsset.objects.create(course=old,title='Protected prior draft resource',asset_type='learner_guide',storage_path='fixture-only/prior.pdf',status='in_review')
        user=get_user_model().objects.create_user(username='pcei-fixture-learner')
        CourseEnrollment.objects.create(user=user,course=originals[0]);CourseProgress.objects.create(user=user,course=originals[0],best_score=90,status='completed')
        Badge.objects.create(user=user,course=originals[0]);Certificate.objects.create(user=user,school=school)
        before=snapshot()
        with TemporaryDirectory() as tmp:
            receipt=Path(tmp)/'stage.json'
            call_command('stage_authored_review',package=BATCH/'review_package.json',commit=True,receipt=receipt,stdout=io.StringIO())
            proof=read(receipt.with_suffix('.applied.json'));self.assertEqual(before,proof['before']);self.assertEqual(before,proof['after'])
            after=snapshot()
            with self.assertRaises(CommandError):call_command('stage_authored_review',package=BATCH/'review_package.json',commit=True,receipt=Path(tmp)/'replay.json',stdout=io.StringIO())
            self.assertEqual(after,snapshot())
        self.assertEqual(school.courses.count(),8)
        for old in originals:
            old.refresh_from_db();self.assertTrue(old.is_active);self.assertEqual(old.paralearn_assessment_id,'fixture-cbt-'+old.course_code)
        new=school.courses.exclude(pk__in=[c.pk for c in originals]);self.assertEqual(new.count(),5)
        self.assertTrue(all(not c.is_active and not c.paralearn_assessment_id for c in new))
        school.refresh_from_db();self.assertFalse(school.enrollment_open)
