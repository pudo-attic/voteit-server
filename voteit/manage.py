from flask.ext.script import Manager

from voteit.core import db
from voteit.web import app


manager = Manager(app)


def run():
    manager.run()

if __name__ == "__main__":
    run()
