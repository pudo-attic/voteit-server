import json

from flask.ext.script import Manager

from voteit.web import app
from voteit.loader import load_motions


manager = Manager(app)


@manager.command
def loadfile(file_name):
    """ Load motions from a JSON file. """
    with open(file_name, 'rb') as fh:
        data = json.load(fh)
        load_motions(data.get('motions', []))


def run():
    manager.run()

if __name__ == "__main__":
    run()
