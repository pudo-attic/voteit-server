import json

from flask.ext.script import Manager

from voteit.core import db
from voteit.web import app
from voteit.loader import load_motions


manager = Manager(app)


@manager.command
def loadfile(file_name):
    """ Load motions from a JSON file. """
    with open(file_name, 'rb') as fh:
        data = json.load(fh)

        # very finland-specific ....
        parties = [(p.get('id').rsplit('/', 1)[-1], p)
                   for p in data.get('parties')]
        print "%s Parties" % len(parties)

        people = [(p.get('id'), p) for p in data.get('people')]
        print "%s People" % len(people)

        load_motions(data.get('motions', []), dict(parties), dict(people))


@manager.command
def reset():
    for coll in db.collection_names():
        if coll in ['issues', 'system.indexes', 'system.users']:
            continue
        print coll
        db.drop_collection(coll)


def run():
    manager.run()

if __name__ == "__main__":
    run()
