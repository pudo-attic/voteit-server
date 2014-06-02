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


def get_weight(mdata, option):
    weights = mdata.get('weights', {})
    weight = weights.get(option)
    if weight is None:
        if option == 'yes' and weights.get('no') is not None:
            weight = -1 * weights['no']
        elif option == 'no' and weights.get('yes') is not None:
            weight = -1 * weights['yes']
    return weight or 0


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

        # Aggregate by issue locally.
        for issue, mdata in motion_issues.get(cell.get('motion.motion_id')):

            # Output cell key.
            key = repr([issue.get('_id')] + [cell.get(k) for k in set(blocs)])
            if not key in data:
                data[key] = {
                    'issue': issue,
                    'counts': defaultdict(int),
                    'weighted': defaultdict(int),
                    'bloc': {},
                    'stats': {
                        'num_motions': 0,
                        'num_votes': 0,
                        'max_score': 0,
                        'min_score': 0
                    }
                }

            for option in options:
                v = cell.get('votes').get(option, 0)
                data[key]['counts'][option] += v
                data[key]['weighted'][option] += v * get_weight(mdata, option)
            
            for k, v in cell.items():
                if k in blocs:
                    data[key]['bloc'][k] = v

            data[key]['stats']['num_motions'] += 1
            data[key]['stats']['num_votes'] += cell['num_votes']

            weights = map(lambda x: get_weight(mdata, x), options)
            data[key]['stats']['max_score'] += cell['num_votes'] * max(weights)
            data[key]['stats']['min_score'] += cell['num_votes'] * min(weights)

    return data.values()
