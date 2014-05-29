from flask import request
from flask.ext.cors import cross_origin

from voteit.core import app, motions, vote_events, issues
from voteit.util import jsonify, paginate_cursor, obj_or_404

from werkzeug.exceptions import BadRequest
from bson.objectid import ObjectId


#------
# Issues API
#-------

@app.route('/api/1/issues', methods=['GET'])
@cross_origin(headers=['Content-Type'], methods=['GET', 'POST'])
def list_issues():
    cur = issues.find()
    data = paginate_cursor(cur)

    add_motions(data['results'])

    return jsonify(data)


@app.route('/api/1/issues', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def create_issue():
    issue = request.json
    if '_id' in issue:
        del issue['_id']

    validate_issue(issue)

    issue_id = issues.insert(issue)
    issue['_id'] = issue_id
    return jsonify(issue, status=201)


@app.route('/api/1/issues/<string:id>', methods=['DELETE'])
@cross_origin(headers=['Content-Type'], methods=['DELETE', 'PUT', 'GET'])
def delete_issue(id):
    issues.remove(ObjectId(id))
    return '', 204


@app.route('/api/1/issues/<string:id>')
@cross_origin(headers=['Content-Type'])
def get_issue(id):
    issue = issues.find_one({'_id': ObjectId(id)})
    add_motions([issue])
    return jsonify(issue)


@app.route('/api/1/issues/<string:id>', methods=['PUT'])
@cross_origin(headers=['Content-Type'])
def update_issue(id):
    issue = request.json
    issue['_id'] = ObjectId(id)

    validate_issue(issue)

    issues.save(issue)
    return jsonify(issue)




# -------------------


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


def add_motions(issues):
    for issue in issues:
        for m in issue.get('motions', []):
            # fold in the motion information
            motion = motions.find_one({'motion_id': m['motion_id']})
            m['motion'] = motion or {'motion_id': m['motion_id']}
