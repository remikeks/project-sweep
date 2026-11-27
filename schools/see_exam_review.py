"""SEE offline review contract; cannot issue a credential."""
from schools.written_exam_review import review_written_result


def review_see_result(blueprint, result, *, verified_transport=False):
    return review_written_result(blueprint, result, school_code='SEE', verified_transport=verified_transport)
