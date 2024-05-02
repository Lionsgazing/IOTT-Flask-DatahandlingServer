import json
import secrets
import sqlite3
from time import sleep
from flask import Flask, request, make_response, redirect, url_for
import asyncio
import paho.mqtt.client as mqtt
import db_sql.db_sqlite3 as db

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

# Initialize database
connection, cursor = db.initialize_db()
db.close_connection(connection)


def store_values_in_db(data):
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()
    # Convert single quotes to double quotes
    data_string = data.replace("'", '"')

    # Convert the string to a dictionary
    data_dict = json.loads(data_string)

    # Insert values into tables in the sensor DB
    db.insert_values_humidity(connection, cursor, data_dict['humidity'], data_dict['timestamp'], data_dict['location'])
    db.insert_values_pressure(connection, cursor, data_dict['pressure'], data_dict['timestamp'], data_dict['location'])
    db.insert_values_temperature(connection, cursor, data_dict['temperature'], data_dict['timestamp'],
                                 data_dict['location'])
    db.close_connection(connection)


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
    store_values_in_db(message.payload.decode())
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
    mqtt_client.subscribe("raspberry/#", 1)
    mqtt_client.loop_start()


# Initialize MQTT on app start
init_mqtt()

# Example of how to retrieve sensor values from the database by using the API.
# Only certain values are accepted. The accepted values can be found inside the code.
values = db.fetch_sensor_data("humidity", "h", "aarhus", 1000)
print(len(values))


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

@app.route('/getDataset/')
def get_data_from_db():
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()
    query = f"SELECT * FROM humidity"
    query1 = f"SELECT * FROM temperature"
    query2 = f"SELECT * FROM pressure"
   
   #humidity data fetching
    cursor.execute(query)
    rows = cursor.fetchall()
    humidity_values = [row[0] for row in rows]  
    location = [row[2] for row in rows]  
    timestamps = [row[1] for row in rows]  
    unique_location = list(set(location))

   #temperature data fetching
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    temperature_values = [row[0] for row in rows1]  
    location1 = [row[2] for row in rows1]  
    timestamps1 = [row[1] for row in rows1]  
    unique_location1 = list(set(location1))

   #pressure data fetching
    cursor.execute(query2)
    rows2 = cursor.fetchall()
    pressure_values = [row[0] for row in rows2]  
    location2 = [row[2] for row in rows2]  
    timestamps2 = [row[1] for row in rows2]  
    unique_location2 = list(set(location2))

    data = {
        "location": unique_location,
        "timestamps": timestamps,
        "humidity_values": humidity_values
    }
    data1 = {
        "location": unique_location1,
        "timestamps": timestamps1,
        "temperature_values": temperature_values
    }
    data2 = {
        "location": unique_location2,
        "timestamps": timestamps2,
        "pressure_values": pressure_values
    }

    combined_data = {
        "humdity_data": data,
        "temperature_data": data1,
        "pressure_data": data2
    }
    connection.close()
    return combined_data

if __name__ == "__main__":
    app.run(debug=True, use_reloader=False)
