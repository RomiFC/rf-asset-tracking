'''This is the original code that only connects the MQTT client and prints out exactly what the subscription says,
to both the terminal and a text file saved to my desktop.'''

import paho.mqtt.client as mqttClient
import time

def on_connect(client, userdata, flags, rc):

    if rc == 0:

        print("Connected to broker")

        global Connected                #Use global variable
        Connected = True                #Signal connection

    else:

        print("Connection failed")

def on_message(client, userdata, message):
    print("Message received: " + message.payload.decode('utf-8'))
    with open('/Users/mitchclark/Desktop/test.txt','a+') as f:
         f.write("Message received: " + message.payload.decode('utf-8') + "\n")

Connected = False   #global variable for the state of the connection

broker_address= "192.168.129.11"  #Broker address
port = 1883                         #Broker port
user = ""                    #Connection username
password = ""            #Connection password

client = mqttClient.Client("Python")               #create new instance
client.username_pw_set(user, password=password)    #set username and password
client.on_connect= on_connect                      #attach function to callback
client.on_message= on_message                      #attach function to callback
client.connect(broker_address,port,60) #connect
client.subscribe("dwm/node/5000/uplink/location") #subscribe
client.loop_forever() #then keep listening forever
