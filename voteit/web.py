from flask import request, abort

from voteit.core import app, motions, vote_events, issues
from voteit.util import jsonify, paginate_cursor, obj_or_404

from bson.objectid import ObjectId


@app.route('/api/1')
@app.route('/')
def api_index():
    return jsonify({'status': 'ok'})


@app.route('/api/1/motions')
def motions_index():
    cur = motions.find({}, {'vote_events.votes': False})
    data = paginate_cursor(cur)
    return jsonify(data)


@app.route('/api/1/motions/<object_id>')
def motions_get(object_id):
    obj = motions.find_one({'object_id': object_id})
    obj = obj_or_404(obj)
    return jsonify(obj)


@app.route('/api/1/vote_events')
def vote_events_index():
    cur = vote_events.find({}, {'votes': False})
    data = paginate_cursor(cur)
    return jsonify(data)


@app.route('/api/1/vote_events/<identifier>')
def vote_events_get(identifier):
    obj = vote_events.find_one({'identifier': identifier})
    obj = obj_or_404(obj)
    return jsonify(obj)



#------
# Issues API
#-------

@app.route('/api/1/issues', methods=['GET'])
def list_issues():
    cur = issues.find()
    data = paginate_cursor(cur)
    return jsonify(data)

@app.route('/api/1/issues', methods=['POST'])
def create_issue():
    issue = request.json
    if '_id' in issue:
        del issue['_id']

    issue_id = issues.insert(issue)
    issue['_id'] = issue_id
    return jsonify(issue, status=201)

@app.route('/api/1/issues/<string:id>')
def get_issue(id):
    issue = issues.find_one({'_id': ObjectId(id)})
    return jsonify(issue)

@app.route('/api/1/issues/<string:id>', methods=['PUT'])
def update_issue(id):
    issue = request.json
    issue['_id'] = ObjectId(id)
    issues.save(issue)
    return jsonify(issue)

@app.route('/api/1/issues/<string:id>', methods=['DELETE'])
def delete_issue(id):
    issues.remove(ObjectId(id))
    return '', 204
