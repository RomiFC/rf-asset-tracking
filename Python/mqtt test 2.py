import paho.mqtt.client as mqttClient
import time

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to broker")
        global Connected  # Use global variable
        Connected = True   # Signal connection
    else:
        print("Connection failed")

def on_message(client, userdata, message):
    payload_str = message.payload.decode('utf-8')
    print(payload_str)
    
    # Split the payload into an array using commas
    data_string = payload_str.replace('{"position":{', "" + 'x:', "" + 'y:', "" + 'z:', "" + 'quality:', "")
    data_array = data_string.split(',')
    
    # Print the array elements
    print("Data Array:", data_array)

    with open('/Users/mitchclark/Desktop/test.txt', 'a+') as f:
        f.write("\n" + data_array[0] + " " + data_array[1] + " " + data_array[2] + " " + data_array[3] + "\n")

Connected = False   # Global variable for the state of the connection

broker_address = "192.168.129.11"  # Broker address
port = 1883                         # Broker port
user = ""                           # Connection username
password = ""                       # Connection password

client = mqttClient.Client("Python")               # Create a new instance
client.username_pw_set(user, password=password)    # Set username and password
client.on_connect = on_connect                      # Attach function to callback
client.on_message = on_message                      # Attach function to callback
client.connect(broker_address, port, 60)            # Connect
client.subscribe("dwm/node/5000/uplink/location")  # Subscribe
client.loop_forever()                               # Then keep listening forever
