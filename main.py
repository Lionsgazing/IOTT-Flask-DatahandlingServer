import json
import secrets
from flask import Flask, request, make_response, redirect, url_for

app = Flask(__name__)

@app.route('/', methods=["GET", "POST", "DELETE"])
def index():
    """Main page example with the different methods. Probably only need the 'GET' method for this."""
    if request.method == "GET":
        response = make_response('<p> Main page </p>')

    if request.method == "POST":
        pass

    if request.method == "DELETE":
        pass

    return response

@app.route('/example/')
def quote():
    """Example for a different page location."""
    response = app.make_response("<p> Example page <p>")

    return response
