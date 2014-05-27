from voteit.core import app, motions
from voteit.util import jsonify, paginate_cursor, obj_or_404


@app.route('/api/1')
@app.route('/')
def index():
    return jsonify({'status': 'ok'})


@app.route('/api/1/motions')
def motions_index():
    cur = motions.find({}, {'vote_events.votes': False})
    data = paginate_cursor(cur)
    return jsonify(data)


@app.route('/api/1/motions/<object_id>')
def motions_get(object_id):
    data = obj_or_404(motions.find_one({'object_id': object_id}))
    return jsonify(data)
