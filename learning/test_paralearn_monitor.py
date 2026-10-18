import copy
from unittest.mock import patch
from django.test import SimpleTestCase
from learning.paralearn import ParaLearnClient, ParaLearnProtocolError, ParaLearnResultNotFoundError


class ParaLearnMonitorResolutionTests(SimpleTestCase):
    def setUp(self):
        self.monitor = {'examId':'exam-1', 'candidates':[{
            'id':'candidate-1', 'examId':'exam-1', 'externalAttemptId':'external-1',
            'studentId':'student-1', 'candidatePin':'654321'}],
            'participants':[{'attemptId':'attempt-1','studentId':'student-1','candidatePin':'654321'}]}
        self.args = dict(exam_id='exam-1',candidate_id='candidate-1',external_attempt_id='external-1',student_id='student-1')

    def resolve(self, monitor):
        with patch.object(ParaLearnClient, '_request_json', return_value=monitor):
            return ParaLearnClient().resolve_attempt_id(**self.args)

    def test_exact_mapping_returns_only_provider_attempt_id(self):
        self.assertEqual(self.resolve(self.monitor), 'attempt-1')

    def test_other_exam_is_rejected(self):
        self.monitor['examId']='other'
        with self.assertRaises(ParaLearnProtocolError): self.resolve(self.monitor)

    def test_other_external_reference_or_student_is_rejected(self):
        for field in ['externalAttemptId','studentId','examId']:
            with self.subTest(field=field):
                value=copy.deepcopy(self.monitor); value['candidates'][0][field]='other'
                with self.assertRaises(ParaLearnProtocolError): self.resolve(value)

    def test_duplicate_participant_is_ambiguous(self):
        self.monitor['participants'] *= 2
        with self.assertRaises(ParaLearnProtocolError): self.resolve(self.monitor)

    def test_unstarted_candidate_is_pending(self):
        self.monitor['participants']=[]
        with self.assertRaises(ParaLearnResultNotFoundError): self.resolve(self.monitor)

    def test_matching_name_does_not_allow_wrong_pin_or_student(self):
        for field in ['candidatePin','studentId']:
            with self.subTest(field=field):
                value=copy.deepcopy(self.monitor); value['participants'][0][field]='other'
                with self.assertRaises(ParaLearnResultNotFoundError): self.resolve(value)

    def test_blank_pin_is_rejected_not_joined(self):
        self.monitor['candidates'][0]['candidatePin']=''
        self.monitor['participants'][0]['candidatePin']=''
        with self.assertRaises(ParaLearnProtocolError): self.resolve(self.monitor)
