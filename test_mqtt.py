from time import sleep

import paho.mqtt.client as mqtt

def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe("raspberry/#", 2)

def on_message(client, userdata, msg):
    print(f"Received message: {msg.payload.decode()} on topic {msg.topic}")

client = mqtt.Client()
client.on_connect = on_connect
client.on_message = on_message

client.username_pw_set("rpimqttclienta", "pD2l0bYEw")
client.connect("mqtt.niels-bjorn.dk", 1883, 60)
client.loop_start()

data = {
        "temperature": 20,
        "humidity": 21,
        "pressure": 22,
        "timestamp": 12317
    }

while True:
    client.publish("raspberry/Copenhagen/sense-hat/readings/all_readings", str(data))
    sleep(5)