from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

#Paths 
deviceListPath = r'E:\Projects\Traffic_Fiverr\backend\traffic\files\deviceList.json'
sequenceListPath = r'E:\Projects\Traffic_Fiverr\backend\traffic\files\sequenceList.json'

#GET Methods here
@app.route('/getAllDevices/', methods=['GET'])
def getAllDevices():
    print(f"Received request for all devices")
    try:
        with open(deviceListPath, 'r') as file:
            deviceList = json.load(file)
            if deviceList is None:
                return jsonify({"error": "Device not found"}), 404
        return jsonify(deviceList)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/getAllSequences/', methods=['GET'])
def getAllSequences():
    print(f"Received request for all sequences")
    try:
        with open(sequenceListPath, 'r') as file:
            sequence = json.load(file)
            if sequence is None:
                return jsonify({"error": "Sequence List not found"}), 404
        return jsonify(sequence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/getDevice/<deviceId>', methods=['GET'])
def getDevice(deviceId):
    print(f"Received request for device: {deviceId}")
    try:
        with open(deviceListPath, 'r') as file:
            device = json.load(file).get(deviceId, None)
            if device is None:
                return jsonify({"error": "Device not found"}), 404
        return jsonify(device)
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@app.route('/getSequence/<deviceId>', methods=['GET'])
def getDevice(deviceId):
    print(f"Received request for sequence: {deviceId}")
    try:
        with open(sequenceListPath, 'r') as file:
            sequence = json.load(file).get(deviceId, None)
            if sequence is None:
                return jsonify({"error": "Sequence not found"}), 404
        return jsonify(sequence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


#POST Methods here
@app.route('/addDevice/<deviceId>', methods=['POST']) 
def addDevice(deviceId): #Have to add default sequence as well!
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)
        if deviceId in device_list:
            return jsonify({"error": "Device ID already exists"}), 400
        new_device = request.get_json()
        device_list[deviceId] = new_device

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)
        #Add default sequence now    
        with open(sequenceListPath, 'r') as file:
            sequence_list = json.load(file)
            
        new_sequence = request.get_json()
        sequence_list[deviceId] = {
    "0": { "color": "green", "time": 40 },
    "1": { "color": "yellow", "time": 5 },
    "2": { "color": "red", "time": 40 }
  }

        with open(sequenceListPath, 'w') as file:
            json.dump(sequence_list, file, indent=4)        
        
        return jsonify({"message": "Device added successfully"}), 201

    except FileNotFoundError:
        return jsonify({"error": "Device/Sequence list file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the device/Sequence list file"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

@app.route('/removeDevice/<deviceId>', methods=['POST'])
def removeDevice(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)
        if deviceId not in device_list:
            return jsonify({"error": "Device doesn't exist"}), 400
        del device_list[deviceId]
        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        return jsonify({"message": f"Device {deviceId} removed successfully"}), 200

    except FileNotFoundError:
        return jsonify({"error": "Device list file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the device list file"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500

    
@app.route('/changeSequence/<deviceId>', methods=['POST'])
def changeSequence(deviceId):
    try:
        with open(sequenceListPath, 'r') as file:
            sequence_list = json.load(file)
            
        new_sequence = request.get_json()
        sequence_list[deviceId] = new_sequence

        with open(sequenceListPath, 'w') as file:
            json.dump(sequence_list, file, indent=4)
        return jsonify({"message": "Sequence added successfully"}), 201

    except FileNotFoundError:
        return jsonify({"error": "Sequence list file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the sequence list file"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
if __name__ == '__main__':
    app.run(debug=True)



