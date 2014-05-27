from voteit.core import app
from voteit.util import jsonify


@app.route('/')
def index():
    return jsonify({'message': "hello!"})
