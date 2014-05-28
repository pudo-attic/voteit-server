import json
from datetime import datetime
from bson.objectid import ObjectId

from werkzeug.exceptions import NotFound
from flask import Response, request

from voteit.core import url_for


class JSONEncoder(json.JSONEncoder):
    """ This encoder will serialize all entities that have a to_dict
    method by calling that method and serializing the result. """

    def __init__(self, index=False):
        self.index = index
        super(JSONEncoder, self).__init__()

    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat() + 'Z'
        if isinstance(obj, ObjectId):
            return unicode(obj)
        return json.JSONEncoder.default(self, obj)


def hateoas_apply(obj):
    if '@type' in obj:
        _type = obj.pop('@type')
        if _type == 'Motion':
            obj['api_url'] = url_for('motions_get',
                                     motion_id=obj.get('motion_id'))
        if _type == 'VoteEvent':
            obj['api_url'] = url_for('vote_events_get',
                                     identifier=obj.get('identifier'))
        if _type == 'Issue':
            obj['api_url'] = url_for('get_issue',
                                     id=obj.get('id', obj.get('_id')))

    return obj


def hateoas_recurse(obj):
    if isinstance(obj, dict):
        for i, v in obj.items():
            hateoas_recurse(v)
        hateoas_apply(obj)
    elif isinstance(obj, (list, tuple)):
        for o in obj:
            hateoas_recurse(o)


def jsonify(obj, status=200, headers=None, index=False, encoder=JSONEncoder):
    """ Custom JSONificaton to support obj.to_dict protocol. """
    hateoas_recurse(obj)
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
