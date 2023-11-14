import datetime
import os
import csv
import time  # Import the time module

tag_node_id = 5000  # Initialize tag_node_id as a global variable
payload_str = '{"position":{"x":1.00001 "y":1.00001 "z":1.00001 "quality":60 "superFrameNumber":500}'

def handle_message():
    global tag_node_id
    global payload_str
    print(f"Tag Node ID: {tag_node_id}")
    print(payload_str)
    
    char_remove = {'{"position":{': "", '"x":': "", '"y":': "", '"z":': "", '"quality":': "", '"superFrameNumber":': "", "}": ""} 
    # Parses all of the unwanted information from the payload

    data_string = payload_str
    for key, value in char_remove.items():
        data_string = data_string.replace(key, value)
    
    data_array = data_string.split(' ')

    script_dir = os.path.dirname(os.path.realpath(__file__))
    file_path = os.path.join(script_dir, 'test.csv')

    with open(file_path, 'a+', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        formatted_data = [f"{'{:%Y-%m-%d %H:%M:%S}'.format(datetime.datetime.now())} {tag_node_id}"] + data_array
        csv_writer.writerow(formatted_data)

# Run the code in a loop every 5 seconds
while True:
    handle_message()
    time.sleep(5)  # Introduce a 5-second delay
