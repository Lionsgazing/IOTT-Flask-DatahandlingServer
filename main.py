import json
import secrets
from time import sleep
from flask import Flask, request, make_response, redirect, url_for
import asyncio
import paho.mqtt.client as mqtt


app = Flask(__name__)

# MQTT Configuration
MQTT_BROKER = "mqtt.niels-bjorn.dk"
MQTT_PORT = 1883
USERNAME = "rpimqttclienta"
PASSWORD = "pD2l0bYEw"
LAST_WILL_MESSAGE = "Server communication down"
LAST_WILL_TOPIC = "server/status"

# Create the MQTT Client
mqtt_client = mqtt.Client()



def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    if rc == 0:
        print("Connected successfully to MQTT broker")
        # Subscribe only if it's the first connection
        if not hasattr(client, 'is_subscribed'):
            client.subscribe("raspberry/#")
            client.is_subscribed = True
    else:
        print(f"Failed to connect, return code {rc}")

def on_message(client, userdata, message):
    print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")


def on_disconnect(client, userdata, rc):
    if rc != 0:
        print("Unexpected disconnection.")
        # Attempt to reconnect
        try:
            print("Trying to reconnect...")
            client.reconnect()
        except Exception as e:
            print(f"Reconnection failed: {e}")
    else:
        print("Disconnected successfully.")


# Initialize MQTT Client
def init_mqtt():
    mqtt_client.username_pw_set(USERNAME, PASSWORD)
    mqtt_client.on_connect = on_connect
    mqtt_client.on_message = on_message
    mqtt_client.on_disconnect = on_disconnect

    mqtt_client.will_set(LAST_WILL_TOPIC, payload=LAST_WILL_MESSAGE, qos=1, retain=False)

    mqtt_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqtt_client.subscribe("raspberry/#", 0)
    mqtt_client.loop_start()


# Initialize MQTT on app start
init_mqtt()


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

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)