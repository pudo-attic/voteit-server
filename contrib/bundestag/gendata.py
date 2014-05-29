from pprint import pprint
from hashlib import sha1
import json
import re
from collections import defaultdict
from slugify import slugify


VOTE_TYPES = {
    'Ja': 'yes',
    'Nein': 'no',
    'Nicht abg': 'absent',
    'Nichtabg': 'absent',
    'Enthaltung': 'abstain'
}


def load_persons(file_name):
    persons, parties = {}, {}
    with open(file_name, 'rb') as fh:
        data = json.load(fh)
        for d in data.get('results'):
            out = {'memberships': [], 'identifiers': [], 'links': []}
            p = d['partei']
            if p is not None and p != 'fraktionslos':
                pid = 'popit.bundestag/party/%s' % slugify(p)
                if pid not in parties:
                    parties[pid] = {
                        'id': pid,
                        'classification': 'party',
                        'name': p
                    }
                out['party_id'] = pid
                out['memberships'].append({
                    'organization_id': pid,
                    'role': 'member'
                })

            if d['slug'] is None:
                continue

            pid = 'popit.bundestag/person/%s' % d.pop('slug')
            out['id'] = pid

            out['identifiers'].append({
                'identifier': d.pop('fingerprint'),
                'scheme': 'offenesparlament.de'
                })

            name = '%s %s %s %s' % (d['titel'] or '', d['vorname'],
                                    d['adelstitel'] or '', d['nachname'])
            name = re.sub(r'\s+', ' ', name).strip()
            out['name'] = name
            out['family_name'] = d.pop('nachname')
            out['first_name'] = d.pop('vorname')
            out['birth_date'] = d.pop('geburtsdatum')
            out['state'] = d.pop('land')
            ges = d.pop('geschlecht') or ''
            fem_b = 'eiblich' in ges
            out['gender'] = 'female' if fem_b else 'male'
            out['biography'] = d.pop('bio')

            out['links'].append({
                'url': d.pop('bio_url'),
                'note': 'Official profile'
            })
            out['links'].append({
                'url': d.pop('source_url'),
                'note': 'XML profile data'
            })

            f = d.pop('foto_url')
            if f is not None:
                out['image'] = f

            f = d.pop('mdb_id')
            if f is not None:
                out['identifiers'].append({
                    'identifier': f,
                    'scheme': 'bundestag.de'
                    })


            #print d.keys()
            #print d['bio_url']
            print pid
            
            persons[pid] = out
    with open('parties.json', 'wb') as fh:
        json.dump(parties.values(), fh, indent=2)
    with open('people.json', 'wb') as fh:
        json.dump(persons.values(), fh, indent=2)
    return persons, parties


def load_votes(file_name, persons, parties):
    motions_data = dict()
    with open(file_name, 'rb') as fh:
        for vote in json.load(fh).get('results'):
            #print vote
            if not vote['matched'] or vote['fingerprint'] is None:
                continue
            key = vote.get('source_url')
            m = motions_data.get(key)
            if m is None:
                id_ = sha1(key).hexdigest()[:15]
                m = {
                    '@type': 'Motion',
                    'organization': {
                        'id': 'bundestag',
                        'name': 'Deutscher Bundestag'
                    },
                    'sources': {
                        'url': vote.get('source_url')
                    },
                    'context': {
                    },
                    'counts': defaultdict(int),
                    'text': vote.get('subject'),
                    'title': vote.get('title'),
                    'date': vote.get('date'),
                    'motion_id': 'motion-%s' % id_,
                    'result': 'unhappiness',
                    'vote_events': [{
                        '@type': 'VoteEvent',
                        'identifier': 've-%s' % id_,
                        'motion': {
                            'text': vote.get('subject')
                        },
                        'start_date': vote.get('date'),
                        'counts': [],
                        'votes': [],
                    }],
                }

            option = VOTE_TYPES.get(vote['vote'])
            m['counts'][option] += 1

            person = None
            for p in persons.values():
                for ident in p.get('identifiers'):
                    if ident['identifier'] == vote['fingerprint']:
                        person = p

            if person is None:
                continue

            v = {
                '@type': 'Vote',
                'option': option,
                'voter_id': person['id'],
                'party_id': person.get('party_id'),
                'voter_event_id': m['vote_events'][0]['identifier'],
            }
            m['vote_events'][0]['votes'].append(v)

            #pprint(m)
            #if vote['vote'] not in VOTE_TYPES:
            #    print vote['vote']
            motions_data[key] = m

    motions = []
    for motion in motions_data.values():
        counts = motion.pop('counts')
        for option, count in counts.items():
            motion['vote_events'][0]['counts'].append({
                '@type': 'Count',
                'option': option,
                'count': count
            })
        motions.append(motion)

    with open('motions.json', 'wb') as fh:
        json.dump({'motions': motions, 'people': persons, 'parties': parties},
                  fh, indent=2)

if __name__ == '__main__':
    persons, parties = load_persons('data/persons.json')
    load_votes('data/votes.json', persons, parties)
