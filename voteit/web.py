from voteit.core import app


@app.route('/')
def index():
    return "hello!"
