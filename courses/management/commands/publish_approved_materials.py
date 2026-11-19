"""Publish the owner's approved 31-course material release without changing CBTs."""
import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone

from courses.material_publication import (
    load_entries, preflight, protected_snapshot, lifecycle_state,
    verify_remote_resources, publish_atomically,
)


class Command(BaseCommand):
    help = __doc__

    def add_arguments(self, parser):
        parser.add_argument('--approval', type=Path, required=True)
        parser.add_argument('--receipt', type=Path, required=True)
        parser.add_argument('--commit', action='store_true')

    def handle(self, *args, **options):
        approval = json.loads(options['approval'].read_text(encoding='utf-8'))
        if (approval.get('scope') != 'SWP-035-SWP-065 materials and individual course access'
                or not approval.get('owner_statement', '').strip()
                or not approval.get('approved_on', '').strip()):
            raise CommandError('Explicit owner approval and release scope are required')
        receipt = options['receipt']
        if receipt.exists() or receipt.with_suffix('.applied.json').exists():
            raise CommandError('Publication journal exists; inspect outcomes instead of replaying')
        root = Path(__file__).resolve().parents[3]/'production_courseware'
        entries = load_entries(root)
        course_ids, asset_ids, resources = preflight(entries)
        before = lifecycle_state(course_ids, asset_ids)
        protected = protected_snapshot(course_ids, asset_ids)
        receipt.parent.mkdir(parents=True, exist_ok=True)
        intent = dict(status='verification_pending', approval=approval, course_ids=sorted(course_ids),
                      asset_ids=sorted(asset_ids), before=json.loads(json.dumps(before, default=str)),
                      protected=protected, timestamp=timezone.now().isoformat())
        with receipt.open('x', encoding='utf-8') as handle:
            json.dump(intent, handle, indent=2)
        verified = verify_remote_resources(resources)
        self.stdout.write(f'Verified {len(verified)} exact private remote material hashes.', ending='\n')
        if not options['commit']:
            self.stdout.write('Preflight passed; no course or material publication changed.')
            return
        after = publish_atomically(course_ids, asset_ids, before, protected)
        result = dict(status='owner_approved_published', approval=approval, course_ids=sorted(course_ids),
                      asset_ids=sorted(asset_ids), remote_hashes=verified, protected=protected,
                      protected_parity=True, before=before, after=after,
                      timestamp=timezone.now().isoformat(),
                      attribution='Explicit owner instruction recorded in approval receipt; no reviewer account impersonated.')
        with receipt.with_suffix('.applied.json').open('x', encoding='utf-8') as handle:
            json.dump(result, handle, indent=2, default=str)
        self.stdout.write(f'Published {len(asset_ids)} resources and activated {len(course_ids)} courses. Teaching, CBTs, schools, learners and credentials preserved.')
