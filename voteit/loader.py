from pprint import pprint

from voteit.core import motions, vote_events
from voteit.core import vote_counts, votes


def load_motions(motions_data):
    
    for motion in motions_data:
        motion['@type'] = 'Motion'
        for e in motion['vote_events']:
            e['@type'] = 'VoteEvent'
            for c in e['counts']:
                e['@type'] = 'VoteCount'
            for v in e['votes']:
                e['@type'] = 'Vote'

        motions.update({'object_id': motion.get('object_id')},
                       motion, upsert=True)
        vote_events_data = motion.get('vote_events')
        #pprint(vote_events)

        for vote_event in vote_events_data:
            vote_event_id = vote_event.get('identifier')
            vote_events.update({'identifier': vote_event_id},
                               vote_event, upsert=True)
            
            for count in vote_event.get('counts'):
                count['vote_event_id'] = vote_event_id
                vote_counts.update({'vote_event_id': vote_event_id, 'option': count.get('option')},
                                   count, upsert=True)

            for vote in vote_event.get('votes'):
                vote['vote_event_id'] = vote_event_id
                votes.update({'vote_event_id': vote_event_id, 'voter_id': count.get('voter_id')},
                             vote, upsert=True)
