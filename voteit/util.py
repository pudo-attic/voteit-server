import json
from datetime import datetime
from bson.objectid import ObjectId

from werkzeug.exceptions import NotFound
from flask import Response, request


class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def __init__(self, index=False):
        self.index = index
        super(JSONEncoder, self).__init__()

    def default(self, obj):
        if self.index and hasattr(obj, 'to_dict_index'):
            return obj.to_dict_index()
        if hasattr(obj, 'to_dict'):
            return obj.to_dict()
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        if isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)


def jsonify(obj, status=200, headers=None, index=False, encoder=JSONEncoder):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    if encoder is JSONEncoder:
        data = encoder(index=index).encode(obj)
    else:
        data = encoder().encode(obj)
    if 'callback' in request.args:
        cb = request.args.get('callback')
        data = '%s && %s(%s)' % (cb, cb, data)
    return Response(data, headers=headers,
                    status=status,
                    mimetype='application/json')


def paginate_cursor(cur):
    # TODO validation:
    limit = int(request.args.get('limit', '25'))
    offset = int(request.args.get('offset', '0'))
    data = {
        'count': cur.count(),
        'limit': limit,
        'offset': offset
    }
    cur.limit(limit)
    cur.skip(offset)
    data['results'] = list(cur)
    return data


def obj_or_404(obj):
    if obj is None:
        raise NotFound()
    return obj
