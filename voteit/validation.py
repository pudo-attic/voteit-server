
from werkzeug.exceptions import BadRequest

def validate_issue(issue):
    # {
    #     "id": "538471046cd78c831e93e17a",
    #     "title": "Issue title",
    #     "phrase": "Issue phrase",
    #     "motions": [
    #         {
    #             "motion": {"motion_id": "abc123"},
    #             "weights": {"yes": 10}
    #         },
    #     ]
    # }

    for key in ['phrase', 'title']:
        if not issue.get(key):
            raise BadRequest('Issue must have a non-empty "%s"' % key)

    if not 'motions' in issue:
        raise BadRequest('Issue must have a "motions" key')

    validate_issue_motions(issue['motions'])


def validate_issue_motions(motions):
    for m in motions:
        # motion: {
        #   id: "abc123",
        #   ...
        # }
        if not 'motion' in m or not m['motion'].get('motion_id'):
            raise BadRequest('motion must have a "motion" object with a non-empty "motion_id"')
        motion_id = m['motion']['motion_id']

        # clean out everything except the id
        m['motion'] = {"motion_id": motion_id}
        m['motion_id'] = motion_id

        # weights: {
        #   yes: 2,
        #   no: -1,
        # }
        if not 'weights' in m or not m['weights']:
            raise BadRequest('motion %s must have a "weights" object with at least one key' % motion_id)
