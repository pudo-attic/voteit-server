from collections import defaultdict

from bson.code import Code
from bson.objectid import ObjectId

from voteit.core import votes, issues

REDUCE = Code("""
function(obj, prev) {
    if (!prev.votes.hasOwnProperty(obj.option)) {
        prev.votes[obj.option] = 0;
    }
    prev.votes[obj.option] += obj.weight;
    prev.num_votes += obj.weight;
};
""")


def get_options():
    options = votes.find({}).distinct('option')
    return options

def generate_aggregate(blocs=[], issue_ids=[], filters={}):
    keys = set(blocs)
    _filt = {}
    if len(issue_ids):
        _filt = {'_id': {'$in': [ObjectId(i) for i in issue_ids]}}
    issue_objs = list(issues.find(_filt))

    motion_issues = defaultdict(list)
    for issue in issue_objs:
        for motion in issue.get('motions', []):
            motion_issues[motion['motion_id']].append((issue, motion))

    spec = dict(filters)
    spec['motion.motion_id'] = {'$in': motion_issues.keys()}
    keys.add('motion.motion_id')

    options = get_options()

    data = {}
    # Aggregate on the server.
    for cell in votes.group(keys, spec, {"votes": {}, 'num_votes': 0}, REDUCE):

        key = repr([cell.get(k) for k in set(blocs)])
        if not key in data:
            data[key] = {
                'key': key,
                'motions': motion_issues.keys(),
                'counts': defaultdict(int),
                'bloc': {},
                'stats': {
                    'num_motions': 0,
                    'num_votes': 0
                }
            }

        for option in options:
            v = cell.get('votes').get(option, 0)
            data[key]['counts'][option] += v
        
        for k, v in cell.items():
            if k in blocs:
                data[key]['bloc'][k] = v

        data[key]['stats']['num_motions'] += 1
        data[key]['stats']['num_votes'] += cell['num_votes']

    return data.values()
