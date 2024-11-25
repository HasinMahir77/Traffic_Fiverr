from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import time
import threading

app = Flask(__name__)
CORS(app)

# Paths
deviceListPath = r'backend/traffic/files/deviceList.json'
sequenceListPath = r'backend/traffic/files/sequenceList.json'


# Function to periodically check device statuses
def monitor_device_status():
        try:
            with open(deviceListPath, 'r') as file:
                device_list = json.load(file)

            current_time = time.time()
            for device_id, device in device_list.items():
                last_reply = device.get("lastReply", 0)
                if current_time - last_reply > 2:  # Check if more than 2 seconds
                    device["status"] = 0  # Set status to 0

            with open(deviceListPath, 'w') as file:
                json.dump(device_list, file, indent=4)

        except Exception as e:
            print(f"Error monitoring device statuses: {e}")

        #time.sleep(2)  # Check every 2 seconds


# Start the monitoring function in a separate thread
threading.Thread(target=monitor_device_status, daemon=True).start()


# GET Methods
@app.route('/getAllDevices/', methods=['GET'])
def getAllDevices():
    try:
        with open(deviceListPath, 'r') as file:
            deviceList = json.load(file)
        return jsonify(deviceList)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getAllSequences/', methods=['GET'])
def getAllSequences():
    try:
        with open(sequenceListPath, 'r') as file:
            sequence = json.load(file)
        return jsonify(sequence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getDevice/<deviceId>', methods=['GET'])
def getDevice(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device = json.load(file).get(deviceId)
        if not device:
            return jsonify({"error": "Device not found"}), 404
        return jsonify(device)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getSequence/<deviceId>', methods=['GET'])
def getSequence(deviceId):
    try:
        with open(sequenceListPath, 'r') as file:
            sequence = json.load(file).get(deviceId)
        if not sequence:
            return jsonify({"error": "Sequence not found"}), 404
        return jsonify(sequence)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/getStatus/<deviceId>', methods=['GET'])
def getStatus(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            deviceList = json.load(file)

        device = deviceList.get(deviceId)
        if not device:
            return jsonify({"error": "Device not found"}), 404

        if (time.time()-deviceList[deviceId]["lastReply"]>0.5):
            deviceList[deviceId]["status"] = 0
        else:
            deviceList[deviceId]["status"] = 1
        
        response = {
            "mode": device["mode"],
            "color": device.get("color"),
            "timeLeft": device.get("timeLeft"),
            "manualColor": device.get("manualColor"),
            "status": device.get("status", 0),
        }
        return jsonify(response)
    except Exception as e:
        return jsonify({"error": str(e)}), 500



# POST Methods
@app.route('/addDevice/<deviceId>', methods=['POST'])
def addDevice(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)
        if deviceId in device_list:
            return jsonify({"error": "Device ID already exists"}), 400

        new_device = request.get_json()
        new_device["color"] = "yellow"
        new_device["timeLeft"] = 0
        new_device["mode"] = "auto"
        new_device["manualColor"] = "yellow"
        device_list[deviceId] = new_device

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        with open(sequenceListPath, 'r') as file:
            sequence_list = json.load(file)

        new_sequence = {
            "0": {"color": "green", "time": 40},
            "1": {"color": "yellow", "time": 5},
            "2": {"color": "red", "time": 40},
        }
        sequence_list[deviceId] = new_sequence

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

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/changeSequence/<deviceId>', methods=['POST'])
def changeSequence(deviceId):
    try:
        # Load the current sequence list
        with open(sequenceListPath, 'r') as file:
            sequence_list = json.load(file)

        # Get the new sequence from the request
        new_sequence = request.get_json()
        print(new_sequence)

        # Transform the list format to the desired dictionary format with integer times
        if isinstance(new_sequence, list):
            transformed_sequence = {
                str(index): {
                    "color": step["color"],
                    "time": int(step["time"])  # Ensure 'time' is cast to integer
                }
                for index, step in enumerate(new_sequence)
            }
        else:
            return jsonify({"error": "Invalid format for sequence"}), 400

        # Update the sequence for the given device ID
        sequence_list[deviceId] = transformed_sequence

        # Save the updated sequence list
        with open(sequenceListPath, 'w') as file:
            json.dump(sequence_list, file, indent=4)

        return jsonify({"message": "Sequence updated successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



@app.route('/setState/<deviceId>', methods=['POST'])
def setState(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)

        if deviceId not in device_list:
            return jsonify({"error": "Device doesn't exist"}), 400

        newState = request.get_json()
        device_list[deviceId]["color"] = newState["color"]
        device_list[deviceId]["timeLeft"] = newState["timeLeft"]

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        return jsonify({"message": "State set successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/setManualColor/<deviceId>', methods=['POST'])
def setManualColor(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)

        if deviceId not in device_list:
            return jsonify({"error": "Device doesn't exist"}), 400

        data = request.get_json()
        device_list[deviceId]["manualColor"] = data["manualColor"]

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        return jsonify({"message": "Manual color set"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/setMode/<deviceId>', methods=['POST'])
def setMode(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)

        if deviceId not in device_list:
            return jsonify({"error": "Device doesn't exist"}), 400

        data = request.get_json()
        device_list[deviceId]["mode"] = data["mode"]

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        return jsonify({"message": "Mode set successfully"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route('/setLastReply/<deviceId>', methods=['POST'])
def setLastReply(deviceId):
    try:
        with open(deviceListPath, 'r') as file:
            device_list = json.load(file)

        if deviceId not in device_list:
            return jsonify({"error": "Device doesn't exist"}), 400

        data = request.get_json()

        if data.get("connected") == 1:
            lastReply = time.time()
            device_list[deviceId]["lastReply"] = lastReply

        with open(deviceListPath, 'w') as file:
            json.dump(device_list, file, indent=4)

        print(f"Updated status for {deviceId}: {device_list[deviceId]['status']}")  # Debug log
        return jsonify({"message": f"Got last reply from {deviceId}"}), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500



if __name__ == '__main__':
    app.run(debug=False, threaded=True, host='0.0.0.0')
