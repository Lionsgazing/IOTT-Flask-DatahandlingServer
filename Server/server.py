import json
import secrets
import sqlite3
from time import sleep
from flask import Flask, request, make_response, redirect, url_for, Response
import asyncio
import paho.mqtt.client as mqtt
import db_sql.db_sqlite3 as db
from datetime import datetime, timedelta

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


def store_values_in_db(data: str, location: str):
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()
    # Convert single quotes to double quotes
    data_string = data.replace("'", '"')

    # Convert the string to a dictionary
    data_dict = json.loads(data_string)

    # Insert values into tables in the sensor DB
    db.insert_values_humidity(connection, cursor, data_dict['humidity'], data_dict['timestamp'], location)
    db.insert_values_pressure(connection, cursor, data_dict['pressure'], data_dict['timestamp'], location)
    db.insert_values_temperature(connection, cursor, data_dict['temperature'], data_dict['timestamp'], location)
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


def on_message(client, userdata, message: mqtt.MQTTMessage):
    #Get location from topic
    location = message.topic.split("/")[1]

    store_values_in_db(message.payload.decode(), location)
    #print(f"Received message '{message.payload.decode()}' on topic '{message.topic}'")


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
    mqtt_client.subscribe("raspberry/Odense/sense-hat/readings/all_readings", 1)
    mqtt_client.subscribe("raspberry/Aalborg/sense-hat/readings/all_readings", 1)
    mqtt_client.subscribe("raspberry/Aarhus/sense-hat/readings/all_readings", 1)
    mqtt_client.subscribe("raspberry/Silkeborg/sense-hat/readings/all_readings", 1)
    mqtt_client.subscribe("raspberry/Copenhagen/sense-hat/readings/all_readings", 1)
    
    mqtt_client.loop_start()


# Initialize MQTT on app start
init_mqtt()

#connection = sqlite3.connect("SensorValues.db")
#cursor = connection.cursor()
#query = f"DELETE FROM humidity"
#query1 = f"DELETE FROM temperature"
#query2 = f"DELETE FROM pressure"
#cursor.execute(query)
#cursor.execute(query1)
#cursor.execute(query2)
#connection.commit()


# Example of how to retrieve sensor values from the database by using the API.
# Only certain values are accepted. The accepted values can be found inside the code.
def get_chunk_of_data(location, hours_back):
    humidity_data = db.fetch_sensor_data("humidity", "h", location, hours_back)
    temperature_data = db.fetch_sensor_data("temperature", "t", location, hours_back)
    pressure_data = db.fetch_sensor_data("pressure", "p", location, hours_back)
    data_chunk = {
        'location': location,
        'hours_back': hours_back,
        'temperature': [temperature[0] for temperature in temperature_data],
        'humidity': [humidity[0] for humidity in humidity_data],
        'pressure': [pressure[0] for pressure in pressure_data]
    }

    return data_chunk


get_chunk_of_data('aarhus', 1000)


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


@app.route("/database", methods=["GET", "POST", "DELETE"])
def request_database():
    if (request.method == "GET"):
        location = request.args.get("location")
        hours_back = request.args.get("hours_back")
        return database_get_data(location, hours_back)
    
    elif (request.method == "POST"):
        #Get args
        #Alter database
        return database_post_data()

    elif (request.method == "DELETE"):
        #Get args
        location = request.args.get("location")
        hours_back = request.args.get("hours_back")

        #Alter database
        return database_delete_data()

    else:
        # Do nothing
        return ""

def database_get_data(location: str, hours_back: int):
    if hours_back == None:
        hours_back = 12

    if location == None:
        # Return all known locations
        known_locations = ["Copenhagen", "Odense", "Silkeborg", "Aalborg", "Aarhus"]

        payload = {}
        for location in known_locations:
            payload.update({location: get_chunk_of_data(location, hours_back)})

        return payload
    else:
        payload = {
            location: get_chunk_of_data(location, hours_back)
        }

        return payload

def database_post_data(location: str, timestamp: int, value: float):
    pass

def database_delete_data(location: str, hours_back: int):
    # Check passed values
    if (hours_back == None):
        return False
    
    if (location == None):
        return False

    # Calculate target datetime
    target_datetime = datetime.now() - timedelta(hours=hours_back)

    # Connect to database
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()

    # Create query
    query = f"DELETE FROM {location} WHERE timestamp >= {target_datetime.timestamp()}"

    # Execute and commit changes
    cursor.execute(query)
    connection.commit()

    return True


@app.route('/getDataset/')
def get_data_from_db():
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()
    query = f"SELECT * FROM humidity"
    query1 = f"SELECT * FROM temperature"
    query2 = f"SELECT * FROM pressure"

    # humidity data fetching
    cursor.execute(query)
    rows = cursor.fetchall()
    humidity_values = [row[0] for row in rows]
    location = [row[2] for row in rows]
    timestamps = [row[1] for row in rows]
    unique_location = list(set(location))

    # temperature data fetching
    cursor.execute(query1)
    rows1 = cursor.fetchall()
    temperature_values = [row[0] for row in rows1]
    location1 = [row[2] for row in rows1]
    timestamps1 = [row[1] for row in rows1]
    unique_location1 = list(set(location1))

    # pressure data fetching
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
