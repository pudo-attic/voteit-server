import json

from flask.ext.script import Manager

from voteit.core import db
from voteit.web import app
from voteit.loader import load_motions
from voteit.loader import load_parties, load_people


manager = Manager(app)


@manager.command
def loadfile(file_name):
    """ Load motions from a JSON file. """
    with open(file_name, 'rb') as fh:
        data = json.load(fh)
        load_parties(data)
        load_people(data)
        load_motions(data)


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
