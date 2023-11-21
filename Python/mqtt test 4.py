'''This is update 4, as of 11-14-23 this is the most updated code that fixes a big bug that we've had for a while.
Instead of giving an error everytime the code runs, when it cant connect to the MQTT server.
The code will now just keep trying to reconnect until it does connect, rather than crashing.
This is great if the internet goes down at the facility, rather than the code failing, it will just try to reconnect.

Updated the error handling of the code, also added a timer so the tags will communicate at whatever rate we set them to, but
rather than recieving the payload at that rate, we have a delay to recieve them slower. per Dan'''

import paho.mqtt.client as mqttClient
import time
import datetime
import os

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected
        Connected = True
    else:
        print(f"Connection failed with result code {rc}")
        client.reconnect()

def on_message(client, userdata, message, tag_node_id):
    payload_str = message.payload.decode('utf-8')
    topic = message.topic
    print(f"Tag Node ID: {tag_node_id}")
    print(payload_str)
    
    char_remove = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", '"superFrameNumber":': "", "}": ""} 
    data_string = payload_str
    for key, value in char_remove.items():
        data_string = data_string.replace(key, value)
    
    data_array = data_string.split(' ')

    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.txt')

    with open(file_path, 'a+') as f:
        formatted_data = ",".join(data_array)
        f.write(f"\n {'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())} {tag_node_id},{formatted_data}\n")

    # Introduce a delay of 1 second (you can adjust this value)
    time.sleep(20)

Connected = False

broker_address = "192.168.68.94"
port = 1883
user = ""
password = ""

client = mqttClient.Client("UWB")
client.username_pw_set(user, password=password)
client.on_connect = on_connect

client.message_callback_add("dwm/node/1911/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, tag_node_id=1911))

while not Connected:
    try:
        client.connect(broker_address, port, 60)
        client.subscribe([("dwm/node/1911/uplink/location", 0)])
        client.loop_forever()
    except OSError:
        print("Connection failed, retrying...")
        time.sleep(5)
