"""CPS offline human-review contract; never issues credentials."""
from schools.written_exam_review import review_written_result


def review_cps_result(blueprint, result, *, verified_transport=False):
    return review_written_result(blueprint, result, school_code='CPS', verified_transport=verified_transport)
