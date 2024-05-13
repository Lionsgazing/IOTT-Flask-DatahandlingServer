import sqlite3
from datetime import datetime, timedelta


def initialize_db():
    # Initialize connection to DB and create cursor
    connection = sqlite3.connect("SensorValues.db")
    cursor = connection.cursor()

    # Generating tables for obtained values from the SenseHat
    res = cursor.execute("SELECT name FROM sqlite_master WHERE name='temperature'")
    if res.fetchone() is None:
        cursor.execute("CREATE TABLE temperature(t, timestamp, location)")

    res = cursor.execute("SELECT name FROM sqlite_master WHERE name='humidity'")
    if res.fetchone() is None:
        cursor.execute("CREATE TABLE humidity(h, timestamp, location)")

    res = cursor.execute("SELECT name FROM sqlite_master WHERE name='pressure'")
    if res.fetchone() is None:
        cursor.execute("CREATE TABLE pressure(p, timestamp, location)")

    res = cursor.execute("SELECT name FROM sqlite_master WHERE name='colour'")
    if res.fetchone() is None:
        cursor.execute("CREATE TABLE colour(red,green, blue, brightness, timestamp, location)")

    return connection, cursor


def close_connection(connection):
    connection.close()


def insert_values_temperature(connection, cursor, temp, timestamp, location):
    cursor.execute("""
        INSERT INTO temperature (t, timestamp,location) VALUES
            (?, ?, ?)
    """, (temp, timestamp, location))

    connection.commit()


def insert_values_humidity(connection, cursor, humi, timestamp, location):
    cursor.execute("""
            INSERT INTO humidity (h, timestamp, location) VALUES
                (?, ?, ?)
        """, (humi, timestamp, location))

    connection.commit()


def insert_values_pressure(connection, cursor, pressure, timestamp, location):
    cursor.execute("""
                INSERT INTO pressure (p, timestamp, location) VALUES
                    (?, ?, ?)
            """, (pressure, timestamp, location))

    connection.commit()


def insert_values_colour(connection, cursor, red, green, blue, brightness, timestamp, location):
    cursor.execute("""
                    INSERT INTO colour (red, green, blue, brightness, timestamp, location) VALUES
                        (?, ?, ?, ?, ?, ?)
                """, (red, green, blue, brightness, timestamp, location))

    connection.commit()

def fetch_sensor_data(table_name, sensor_type, location, hours_back):
    # Connect to the sensor SQLite database
    conn = sqlite3.connect('SensorValues.db')
    cursor = conn.cursor()

    # Calculate the cutoff datetime in Unix time
    cutoff_time = datetime.now() - timedelta(hours=int(hours_back))
    cutoff_unix_time = cutoff_time.timestamp()

    # To avoid SQL injections parameters are listed here
    # to keep the table name and other parameters are safe to use in a query.
    allowed_tables = ["pressure", "humidity", "temperature"]
    allowed_sensors = ["h", "t", "p"]
    allowed_locations = ["aarhus", "silkeborg", "copenhagen", "odense", "Aarhus", "Silkeborg", "Odense", "Aalborg", "Copenhagen"]

    if table_name not in allowed_tables:
        raise ValueError("Invalid table name")
    if sensor_type not in allowed_sensors:
        raise ValueError("Invalid sensor value name")
    if location not in allowed_locations:
        raise ValueError("Invalid location name")

    # Create a query to select data dynamically based on the table name and type of the value.
    query = f"""
                SELECT {sensor_type}, timestamp FROM {table_name}
                WHERE location = ? AND timestamp >= ? order by timestamp asc
                """

    # Execute the query with parameters to ensure proper handling of data types and avoid SQL injections.
    cursor.execute(query, (location, cutoff_unix_time))

    # Fetch all rows of the query.
    rows = cursor.fetchall()

    # Close the connection.
    conn.close()

    # Return a list of sensor values.
    return [((row[0], row[1]), table_name, location) for row in rows]
