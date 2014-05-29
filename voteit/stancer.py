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


def generate_stances(blocs=[], issue_ids=[], filters={}):
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
                    'stance': defaultdict(int),
                    'bloc': {},
                    'stats': {
                        'num_motions': 0,
                        'num_votes': 0,
                        'max_score': 0,
                        'min_score': 0
                    }
                }

            for option in options:
                v = cell.get('votes').get(option, 0) * get_weight(mdata, option)
                data[key]['stance'][option] += v
            
            for k, v in cell.items():
                if k in blocs:
                    data[key]['bloc'][k] = v

            data[key]['stats']['num_motions'] += 1
            data[key]['stats']['num_votes'] += cell['num_votes']

            weights = map(lambda x: get_weight(mdata, x), options)
            data[key]['stats']['max_score'] += cell['num_votes'] * max(weights)
            data[key]['stats']['min_score'] += cell['num_votes'] * min(weights)

    blocs = []
    for bloc in data.values():
        # determine the full range of available values:
        value_range = bloc['stats']['max_score'] - bloc['stats']['min_score']

        # sum up 'yes' and 'no' values:
        bloc_value = sum(bloc['stance'].values())

        # make the bloc value fall in between 0 and value_range
        normalized_value = bloc_value + (bloc['stats']['min_score'] * -1)

        # calculate a score based on the normalized value and the value range
        bloc['match'] = normalized_value / max(1, value_range)
        blocs.append(bloc)
    return blocs
