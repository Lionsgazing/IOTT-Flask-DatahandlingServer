import json
import secrets
from time import sleep
from flask import Flask, request, make_response, redirect, url_for
import asyncio

app = Flask(__name__)

@app.route('/', methods=["GET", "POST", "DELETE"])
def index():
    """Main page example with the different methods. Probably only need the 'GET' method for this."""
    if request.method == "GET":
        # Get example
        response = make_response('<p> Main page </p>')

        # Read data from csv and return it to the user.


    if request.method == "POST":
        # Post example
        pass

    if request.method == "DELETE":
        # Delete example
        pass

    return response

@app.route('/example/')
def quote():
    """Example for a different page location."""
    response = app.make_response("<p> Example page <p>")

    return response