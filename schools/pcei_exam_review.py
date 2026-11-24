"""PCEI offline review compatibility entry point; never issues credentials."""
from schools.written_exam_review import review_written_result


def review_pcei_result(blueprint, result, *, verified_transport=False):
    return review_written_result(blueprint, result, school_code='PCEI', verified_transport=verified_transport)
