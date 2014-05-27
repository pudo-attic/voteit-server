from voteit.core import app, motions, vote_events
from voteit.util import jsonify, paginate_cursor, obj_or_404


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
