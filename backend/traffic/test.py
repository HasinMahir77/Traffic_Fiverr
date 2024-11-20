import json

# Path to the JSON file
deviceListPath = r'E:\Projects\Traffic_Fiverr\backend\traffic\files\deviceList.json'

# Open and read the JSON file
with open(deviceListPath, 'r') as file:
    device = json.load(file)['device1']
# Print the parsed JSON data
print(device)

