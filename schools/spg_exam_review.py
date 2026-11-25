"""SPG offline human-review contract; never issues credentials."""
from schools.written_exam_review import review_written_result


def review_spg_result(blueprint, result, *, verified_transport=False):
    return review_written_result(blueprint, result, school_code='SPG', verified_transport=verified_transport)
