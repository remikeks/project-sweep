"""Offline criterion-level human review for a specified school. Never issues credentials."""
from decimal import Decimal, InvalidOperation
from schools.exam_blueprints import review_result_contract

def review_written_result(blueprint,result,*,school_code,verified_transport=False):
    checked=review_result_contract(blueprint,result,verified_transport=verified_transport)
    reasons=list(checked['reasons'])
    if blueprint.get('school_code')!=school_code:
        reasons.append('Wrong school for written review')
    expected={i['id']:i for i in blueprint['items'] if i['type']!='MCQ'}
    for row in result.get('item_results',[]):
        item=expected.get(row.get('id'))
        if item is None:continue
        marks=row.get('criterion_results',[])
        if len(marks)!=len(item['rubric']) or {r.get('criterion') for r in marks}!={r['criterion'] for r in item['rubric']}:
            reasons.append('Written criterion coverage incomplete');continue
        limits={r['criterion']:r['marks'] for r in item['rubric']}
        total=Decimal(0)
        for r in marks:
            try:
                score=Decimal(str(r.get('score')))
                if isinstance(r.get('score'),bool) or not score.is_finite() or not 0<=score<=limits[r['criterion']]:raise ValueError()
                total+=score
            except (ValueError,InvalidOperation,TypeError):reasons.append('Invalid criterion mark')
            if not isinstance(r.get('rationale'),str) or not r['rationale'].strip():reasons.append('Human criterion rationale missing')
        try:
            if total!=Decimal(str(row.get('score'))):reasons.append('Criterion total differs from item score')
        except InvalidOperation:reasons.append('Invalid item score')
        marker=row.get('human_marker_id');moderator=row.get('human_moderator_id')
        if not moderator or moderator==marker or row.get('moderation_status')!='approved':reasons.append('Independent human moderation missing')
        if not row.get('rubric_version') or not row.get('moderation_rationale'):reasons.append('Human review version or rationale missing')
        # Empty histories are valid; absence is not. Do not invent amendments.
        if not isinstance(row.get('amendment_history'),list) or not isinstance(row.get('appeal_history'),list):reasons.append('Amendment or appeal history missing')
    checked.update(contract_checks_passed=not reasons,reasons=sorted(set(reasons)),certificate_authorised=False)
    return checked
