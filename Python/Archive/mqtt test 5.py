import paho.mqtt.client as mqttClient
import time
import datetime
import os
import csv

# Callback function for when the client connects to the MQTT broker
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        # This is where you add the subscribtion topic for each tag on the network, you just need to change the 4 digit Tag_Node_ID, to the one maching the tag.
        client.subscribe("dwm/node/5000/uplink/location")
    else:
        print(f"Connection failed with result code {rc}")
        client.reconnect()

# Callback function for when a message is received from the MQTT broker
def on_message(client, userdata, message):
    # Decode the payload of the message
    payload_str = message.payload.decode('utf-8')
    
    # Define the tag node ID, add a variable for each tag on the network
    tag_node_id = 5000 
    print(f"Tag Node ID: {tag_node_id}")
    print(payload_str)
    
    # Remove unnecessary characters from the payload string
    remove_chars = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", '"superFrameNumber":': "", "}": ""} 
    data_string = payload_str
    for key, value in remove_chars.items():
        data_string = data_string.replace(key, value)
    
    # Split the payload string into an array
    data_array = data_string.split(' ')


    # If you would like the output to be printed to a .txt file, use this block of code:
    # Set the file path for the .txt file
    '''script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.txt')

    # Write the formatted data to the .txt file
    with open(file_path, 'a+') as f:
        formatted_data = ",".join(data_array)
        f.write(f"\n {'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())} {tag_node_id},{formatted_data}\n")'''


    # If you would like the output to be printed to a .csv file, use this block of code:
    # Set the file path for the .csv file
    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.csv')

    # Write the formatted data to the .csv file
    with open(file_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        formatted_data = [f"{'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())}"] + [tag_node_id] + data_array
        csv_writer.writerow(formatted_data)

    # Introduce a delay of 10 seconds (you can adjust this value)
    time.sleep(10)

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
    print("Disconnecting gracefully...")
    client.disconnect()
    client.loop_stop()
    print("Disconnected.")
