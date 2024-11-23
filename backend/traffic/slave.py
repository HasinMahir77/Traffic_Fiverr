from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
import serial
import socket
import time
import threading

serverIp = "http://192.168.0.236:5000"
arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)

app = Flask(__name__)
CORS(app)

def serialWrite(data):
    arduino.write(f"{data}\n".encode())  
    time.sleep(0.1)  

def serialRead():
    if arduino.in_waiting > 0:  
        data = arduino.readline().decode().strip() 
        return data
    return None

def get_all_devices():
    url = f"{serverIp}/getAllDevices/"
    try:
        response = requests.get(url)
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all devices: {e}")
        return None

def get_all_sequences():
    url = f"{serverIp}/getAllSequences/"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all sequences: {e}")
        return None

def get_device(device_id):
    url = f"{serverIp}/getDevice/{device_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device {url}: {e}")
        return None

def get_sequence(device_id):
    url = f"{serverIp}/getSequence/{device_id}"
    try:
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device {url}: {e}")
        return None

def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json")
        return response.json()["ip"]
    except Exception as e:
        return f"Error: {e}"

def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))  
            local_ip = s.getsockname()[0]  
        return local_ip
    except Exception as e:
        return f"Error: {e}"

def run_sequence(sequence):
    while True:
        for item in sequence.values():
            color = item["color"]
            duration = item["time"]
            
            start_time = time.time()
            serialWrite(color)
            print(f"Sent {color} for {duration} seconds")
            
            while True:
                elapsed_time = time.time() - start_time
                if elapsed_time >= duration:
                    break

@app.route('/get_current_color', methods=['POST'])
def get_current_color():
    global last_send_time, color
    timeLeft = time.time() - last_send_time
    return jsonify({"color": color, "timeLeft": timeLeft})

start_time = 0
elapsed_time = 0
last_send_time = 0
deviceName = None
sequenceList = None
sequence = None
deviceIp = get_local_ip()  
deviceList = get_all_devices()  

def run_flask():
    app.run(threaded=True, host='0.0.0.0')

if __name__ == "__main__":
    # Start Flask server in a separate thread
    flask_thread = threading.Thread(target=run_flask)
    flask_thread.daemon = True
    flask_thread.start()

    # Get deviceName and sequence based on IP
    sequenceList = get_all_sequences()
    for i in deviceList:
        if deviceList[i]["ip"] == deviceIp:
            deviceName = i
            sequence = sequenceList[deviceName]
            print(f"Device Name: {deviceName}")
            print(f"Sequence: {sequence}")
            break
    if not deviceName:
        print("Device not found!")

    current_index = 0
    last_send_time = time.time()
    color = sequence[str(current_index)]["color"]
    duration = sequence[str(current_index)]["time"]
    print(f"Sending {color} for {duration} seconds...")

    serialWrite(color)

    try:
        while True:
            current_time = time.time()
            elapsed_time = current_time - last_send_time

            sequenceList = get_all_sequences()
            newSequence = sequenceList[deviceName]
            if sequence != newSequence:
                sequence = newSequence
                current_index = 0
                print("New Sequence detected. Flashing yellow for 5s")

                flashStartTime = time.time()
                while time.time() - flashStartTime < 5:
                    serialWrite("yellow")
                print("Yellow flash stopped")

            if elapsed_time >= duration:
                current_index += 1
                if current_index > 2:
                    current_index = 0
                color = sequence[str(current_index)]["color"]
                duration = sequence[str(current_index)]["time"]

                print(f"Sending {color} for {duration} seconds...")
                serialWrite(color)

                last_send_time = current_time

            data = serialRead()
            if data:
                print(f"Received: {data}")
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Exiting...")
    finally:
        if arduino and arduino.is_open:
            arduino.close()
            print("Serial connection closed.")
