from flask import Flask, request, jsonify
from flask_cors import CORS
import json

app = Flask(__name__)
CORS(app)

#Paths 
deviceListPath = r'E:\Projects\Traffic_Fiverr\backend\traffic\files\deviceList.json'
sequenceListPath = r'E:\Projects\Traffic_Fiverr\backend\traffic\files\sequenceList.json'

#GET Methods here
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
def addDevice(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)
        if deviceId in device_list:
            return jsonify({"error": "Device ID already exists"}), 400
        new_device = request.get_json()
        device_list[deviceId] = new_device

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)
        return jsonify({"message": "Device added successfully"}), 201

    except FileNotFoundError:
        return jsonify({"error": "Device list file not found"}), 500
    except json.JSONDecodeError:
        return jsonify({"error": "Error decoding the device list file"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500
    
@app.route('/setSequence/<deviceId>', methods=['POST'])
def setSequence(deviceId):
    try:
        with open(sequenceListPath, 'r') as file:
            sequence_list = json.load(file)
        if deviceId in sequence_list:
            return jsonify({"error": "Device ID already exists"}), 400
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


