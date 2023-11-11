import paho.mqtt.client as mqttClient
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True   # Signal connection
    else:
        print("Connection failed")

def on_message(client, userdata, message, subscription_id):
    payload_str = message.payload.decode('utf-8')
    topic = message.topic
    print(f"Subscription ID: {subscription_id}")
    print(payload_str)
    
    char_remove = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", "}": "", '"superFrameNumber":': ""} 

    data_string = payload_str
    for key, value in char_remove.items():
        data_string = data_string.replace(key, value)
    
    data_array = data_string.split(',')

    with open(f'/Users/mitchclark/Desktop/test.txt', 'a+') as f:
        formatted_data = ",".join(data_array)
        f.write(f"\n {subscription_id},{formatted_data}\n")

Connected = False   # Global variable for the state of the connection

broker_address = "192.168.68.94"  # Broker address
port = 1883                         # Broker port
user = ""                           # Connection username
password = ""                       # Connection password

client = mqttClient.Client("Python")               # Create a new instance
client.username_pw_set(user, password=password)    # Set username and password
client.on_connect = on_connect                      # Attach function to callback

# Subscribe with subscription IDs
client.message_callback_add("dwm/node/5000/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, subscription_id=5000))
client.message_callback_add("dwm/node/1916/uplink/location", lambda client, userdata, message: on_message(client, userdata, message, subscription_id=1916))

client.connect(broker_address, port, 60)            # Connect
client.subscribe([("dwm/node/5000/uplink/location", 0),("dwm/node/1916/uplink/location", 0)])  # Subscribe
client.loop_forever()                               # Then keep listening forever
