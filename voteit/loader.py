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

        motions.update({'motion_id': motion.get('motion_id')},
                       motion, upsert=True)
        vote_events_data = motion.get('vote_events')
        #pprint(vote_events)

        for vote_event in vote_events_data:
            vote_event_id = vote_event.get('identifier')
            vote_events.update({'identifier': vote_event_id},
                               vote_event, upsert=True)
            
            for count in vote_event.get('counts'):
                count['vote_event_id'] = vote_event_id
                vote_counts.update({'vote_event_id': vote_event_id,
                                    'option': count.get('option')},
                                   count, upsert=True)

            for vote in vote_event.get('votes'):
                load_vote(vote, vote_event, motion)


def load_vote(vote, vote_event, motion):
    #pprint(vote)
    vote['weight'] = 1
    vote['event'] = vote_event.copy()
    if 'motion' in vote['event']:
        del vote['event']['motion']
    if 'votes' in vote['event']:
        del vote['event']['votes']

    vote['motion'] = motion.copy()
    if 'vote_events' in vote['motion']:
        del vote['motion']['vote_events']

    #pprint(vote)
    votes.update({
                 'event.identifier': vote_event.get('identifier'),
                 'voter_id': vote.get('voter_id')},
                 vote, upsert=True)
    
