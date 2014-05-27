from flask import request, abort
from flask.ext.cors import cross_origin

from voteit.core import app, motions, vote_events, issues
from voteit.util import jsonify, paginate_cursor, obj_or_404
from voteit.stancer import generate_stances

from bson.objectid import ObjectId


@app.route('/api/1')
@app.route('/')
@cross_origin(headers=['Content-Type'])
def api_index():
    return jsonify({'status': 'ok'})


@app.route('/api/1/stances')
@cross_origin(headers=['Content-Type'])
def stances_get():
    blocs = request.args.getlist('bloc')
    issues = request.args.getlist('issue')
    filters = {}
    for criterion in request.args.getlist('filter'):
        if not ':' in criterion:
            continue
        field, value = criterion.split(':', 1)
        filters[field] = value
    data = {
        'request': {
            'blocs': blocs,
            'filters': filters,
            'issues': issues
        },
        'stances': generate_stances(blocs, issues, filters)
    }
    return jsonify(data)


@app.route('/api/1/motions')
@cross_origin(headers=['Content-Type'])
def motions_index():
    cur = motions.find({}, {'vote_events.votes': False})
    data = paginate_cursor(cur)
    return jsonify(data)


@app.route('/api/1/motions/<motion_id>')
@cross_origin(headers=['Content-Type'])
def motions_get(motion_id):
    obj = motions.find_one({'motion_id': motion_id})
    obj = obj_or_404(obj)
    return jsonify(obj)


@app.route('/api/1/vote_events')
@cross_origin(headers=['Content-Type'])
def vote_events_index():
    cur = vote_events.find({}, {'votes': False})
    data = paginate_cursor(cur)
    return jsonify(data)


@app.route('/api/1/vote_events/<identifier>')
@cross_origin(headers=['Content-Type'])
def vote_events_get(identifier):
    obj = vote_events.find_one({'identifier': identifier})
    obj = obj_or_404(obj)
    return jsonify(obj)



#------
# Issues API
#-------

@app.route('/api/1/issues', methods=['GET'])
@cross_origin(headers=['Content-Type'])
def list_issues():
    cur = issues.find()
    data = paginate_cursor(cur)
    return jsonify(data)

@app.route('/api/1/issues', methods=['POST'])
@cross_origin(headers=['Content-Type'])
def create_issue():
    issue = request.json
    if '_id' in issue:
        del issue['_id']

    issue_id = issues.insert(issue)
    issue['_id'] = issue_id
    return jsonify(issue, status=201)

@app.route('/api/1/issues/<string:id>')
@cross_origin(headers=['Content-Type'])
def get_issue(id):
    issue = issues.find_one({'_id': ObjectId(id)})
    return jsonify(issue)

@app.route('/api/1/issues/<string:id>', methods=['PUT'])
@cross_origin(headers=['Content-Type'])
def update_issue(id):
    issue = request.json
    issue['_id'] = ObjectId(id)
    issues.save(issue)
    return jsonify(issue)

@app.route('/api/1/issues/<string:id>', methods=['DELETE'])
@cross_origin(headers=['Content-Type'])
def delete_issue(id):
    issues.remove(ObjectId(id))
    return '', 204
