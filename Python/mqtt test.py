import paho.mqtt.client as mqttClient
import time
import datetime
import os
import csv
import json

# Callback function for when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # This is where you add the subscribtion topic and message for each tag on the network, you just need to change the 4 digit Tag_Node_ID, to the one matching the tag.
        client.message_callback_add("dwm/node/5000/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, tag_node_id=5000))
        client.message_callback_add("dwm/node/1916/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, tag_node_id=1916))
        client.subscribe("dwm/node/5000/uplink/location")
        client.subscribe("dwm/node/1916/uplink/location")
    else:
        print(f"Connection failed with result code {rc}")
        client.reconnect()

# Callback function for when a message is received from the MQTT broker
def on_message(client, userdata, message, tag_node_id):
    # Decode the payload of the message
    payload_str = message.payload.decode('utf-8')

    # Parse JSON data
    payload_json = json.loads(payload_str)

    # Extract position information
    position = payload_json.get('position', {})
    x = position.get('x', '')
    y = position.get('y', '')
    z = position.get('z', '')
    quality = position.get('quality', '')
    superFrameNumber = payload_json.get('superFrameNumber', '')  # Adjusted this line

    # Define the tag node ID, add a variable for each tag on the network
    print(f"Tag Node ID: {tag_node_id}")

    # Print individual coordinates
    print(f"X: {x}, Y: {y}, Z: {z}, Quality: {quality}, SuperFrameNumber: {superFrameNumber}")


    # If you would like the output to be printed to a .txt file, use this block of code:
    # Set the file path for the .txt file
    '''script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.txt')

    # Write the formatted data to the .txt file
    with open(file_path, 'a+') as f:
        formatted_data = (
            f"{'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())} "
            f"{tag_node_id} X:{x}, Y:{y}, Z:{z}, Quality:{quality}, SuperFrameNumber:{superFrameNumber}\n"
        )
        f.write(formatted_data)'''


    # If you would like the output to be printed to a .csv file, use this block of code:
    # Set the file path for the .csv file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.csv')

    # Write the formatted data to the .csv file
    with open(file_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        formatted_data = [
            f"{'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}",
            tag_node_id, x, y, z, quality, superFrameNumber
        ]
        csv_writer.writerow(formatted_data)

    # Introduce a delay of 5 seconds (you can adjust this value)
    time.sleep(5)


# Initialize connection status variable
Connected = False

# MQTT broker configuration
broker_address = "172.20.10.2"
port = 1883
user = ""
password = ""

# Create an MQTT client instance
client = mqttClient.Client("UWB")
client.username_pw_set(user, password=password)
client.on_connect = on_connect
client.on_message = on_message

# Attempt to connect to the MQTT broker with retries
while not Connected:
    try:
        client.connect(broker_address, port, 60)  # the 60 corresponds to the number of seconds before the broker has to reconnect. But during testing, I found it's double this number before the broker must reconnect. I do not know why this is.
        Connected = True  # Assume connection is successful
        client.loop_start()  # Start the loop in the background
    except OSError:
        print("Connection failed, retrying...")
        time.sleep(5)

# Main loop to keep the program running
try:
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("Disconnecting...")
    client.disconnect()
    client.loop_stop()
    print("Disconnected.")
