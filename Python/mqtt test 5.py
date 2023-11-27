'''This update number 5, saves everything to a csv file rather than a txt file'''

import paho.mqtt.client as mqttClient
import time
import datetime
import os
import csv

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        client.subscribe("dwm/node/1911/uplink/location")
    else:
        print(f"Connection failed with result code {rc}")
        client.reconnect()

def on_message(client, userdata, message):
    payload_str = message.payload.decode('utf-8')
    tag_node_id = 1911 
    print(f"Tag Node ID: {tag_node_id}")
    print(payload_str)
    
    char_remove = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", '"superFrameNumber":': "", "}": ""} 
    data_string = payload_str
    for key, value in char_remove.items():
        data_string = data_string.replace(key, value)
    
    data_array = data_string.split(' ')

    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.csv')

    with open(file_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        formatted_data = [f"{'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}"] + [tag_node_id] + data_array
        csv_writer.writerow(formatted_data)

    # Introduce a delay of 1 second (you can adjust this value)
    time.sleep(5)

Connected = False

broker_address = "192.168.68.94"
port = 1883
user = ""
password = ""

client = mqttClient.Client("UWB")
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message

while not Connected:
    try:
        client.connect(broker_address, port, 60)  #the 60 corresponds to the number of seconds before the broker has to reconnect. But during testing i found its double this number before the broker must reconnect. I do not know why this is.
        Connected = True  # Assume connection is successful
        client.loop_start()  # Start the loop in the background
    except OSError:
        print("Connection failed, retrying...")
        time.sleep(5)

try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting gracefully...")
    client.disconnect()
    client.loop_stop()
    print("Disconnected.")