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
};
""")


def get_options(filters):
    options = votes.find(filters).distinct('option')
    return options


def get_weight(mdata, option):
    weights = mdata.get('weights', {})
    weight = weights.get(option)
    if weight is None:
        if option == 'yes' and weights['no'] is not None:
            weight = -1 * weights['no']
        if option == 'no' and weights['yes'] is not None:
            weight = -1 * weights['yes']
    return weight or 0


def generate_stances(blocs=[], issue_ids=[], filters={}):
    keys = set(blocs)
    _filt = {}
    if len(issue_ids):
        _filt = {'_id': {'$in': [ObjectId(i) for i in issue_ids]}}
    issue_objs = list(issues.find(_filt))

    motion_issues = defaultdict(list)
    for issue in issue_objs:
        for motion in issue.get('motions', []):
            mid = motion.get('motion_id')
            motion_issues[mid].append((issue, motion))

    spec = dict(filters)
    spec['motion.motion_id'] = {'$in': motion_issues.keys()}
    keys.add('motion.motion_id')

    options = get_options(spec)

    data = {}
    # Aggregate on the server.
    for cell in votes.group(keys, spec, {"votes": {}}, REDUCE):

        # Aggregate by issue locally.
        for issue, mdata in motion_issues.get(cell.get('motion.motion_id')):

            # Output cell key.
            key = repr([issue.get('_id')] + [cell.get(k) for k in keys])
            if not key in data:
                data[key] = {
                    'issue': issue,
                    'stance': defaultdict(int),
                    'bloc': {},
                    'num_motions': 0
                }
            for option in options:
                v = cell.get('votes').get(option, 0) * get_weight(mdata, option)
                data[key]['stance'][option] += v
            
            for k, v in cell.items():
                if k in blocs:
                    data[key]['bloc'][k] = v

            data[key]['num_motions'] += 1

    return data.values()
