import os
from app import app


# main entrypoint
@app.route("/")
def index():
    return "200"

@app.route("/<string:name>")
def hello(name):
    return f"Hello, {name}!"
