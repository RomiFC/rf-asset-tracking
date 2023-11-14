import paho.mqtt.client as mqttClient
import time
import datetime

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True   # Signal connection
    else:
        print(f"Connection failed with result code {rc}")
        # Retry the connection after a delay
        time.sleep(5)
        client.connect(broker_address, port, 60)

def on_message(client, userdata, message, tag_node_id):
    payload_str = message.payload.decode('utf-8')
    topic = message.topic
    print(f"Tag Node ID: {tag_node_id}")
    print(payload_str)
    
    char_remove = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", '"superFrameNumber":': "", "}": ""} 
    #Parses all of the unwanted information from the payload

    data_string = payload_str
    for key, value in char_remove.items():
        data_string = data_string.replace(key, value)
    
    data_array = data_string.split(' ')

    with open(f'/Users/mitchclark/Desktop/test.txt', 'a+') as f:
        formatted_data = ",".join(data_array)
        f.write(f"\n {'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())} {tag_node_id},{formatted_data}\n")

Connected = False   # Global variable for the state of the connection

broker_address = "172.20.10.3"  # Use Gateway IP address
port = 1883                         # Broker port
user = ""                           # Connection username
password = ""                       # Connection password

client = mqttClient.Client("UWB")               # Create a new instance, this name can be anything, it doesnt matter
client.username_pw_set(user, password=password)    # Set username and password
client.on_connect = on_connect                      # Attach function to callback

# Subscribe with tag node IDs
client.message_callback_add("dwm/node/5000/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, tag_node_id=5000))
client.message_callback_add("dwm/node/1916/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, tag_node_id=1916))

while not Connected:  # Keep trying to connect until successful
    try:
        client.connect(broker_address, port, 60)            # Connect
        client.subscribe([("dwm/node/5000/uplink/location", 0),("dwm/node/1916/uplink/location", 0)])  # Subscribe to tag node ID
        client.loop_forever()                               # Then keep listening forever
    except:
        print("Connection failed, retrying...")
        time.sleep(5)  # Wait for a while before retrying
