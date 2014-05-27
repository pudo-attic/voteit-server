from flask import Flask, url_for as _url_for

from voteit import default_settings


app = Flask(__name__)
app.config.from_object(default_settings)
app.config.from_envvar('VOTEIT_SETTINGS', silent=True)

db = None

def url_for(*a, **kw):
    try:
        return _url_for(*a, _external=True, **kw)
    except RuntimeError:
        return None
