from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import requests
import serial
import socket
import time

serverIp = "http://192.168.0.236:5000"
arduino = serial.Serial(port='COM13', baudrate=9600, timeout=0.1)  
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
            
            # Record the start time when we send the color
            start_time = time.time()
            
            # Send the color once
            serialWrite(color)
            print(f"Sent {color} for {duration} seconds")
            
            # Continue checking elapsed time without blocking
            while True:
                # Calculate elapsed time
                elapsed_time = time.time() - start_time
                if elapsed_time >= duration:
                    break  # Exit the loop after the required duration has passed
                # You can add any other non-blocking tasks you want to perform here
                # (e.g., check serial data, handle other logic, etc.)
@app.route('/get_current_color', methods=['POST'])
def get_current_color():
    global last_send_time, color
    timeLeft = time.time()-last_send_time
    return jsonify({"color": color, "timeLeft": timeLeft})

start_time = 0
elapsed_time = 0
last_send_time = 0
deviceName = None
sequence = None
deviceIp = get_local_ip()  # Get the local IP address
deviceList = get_all_devices()  # Fetch the device list

if __name__ == "__main__":
    app.run(debug=True, threaded=True, host='0.0.0.0')
    # Get deviceName and sequence based on IP
    for i in deviceList:
        if deviceList[i]["ip"] == deviceIp:
            deviceName = i
            sequence = get_sequence(deviceName)[deviceName]
            print(f"Device Name: {deviceName}")
            print(f"Sequence: {sequence}")
            break  # Exit loop once device is found
    if not deviceName:
        print("Device not found!")

    current_index = 0
    last_send_time = time.time()  # Track time when the color was last sent
    color = sequence[str(current_index)]["color"]
    duration = sequence[str(current_index)]["time"]
    print(f"Sending {color} for {duration} seconds...")

    serialWrite(color)  # Send the first color immediately

    # Main loop
    while True:
        current_time = time.time()
        elapsed_time = current_time - last_send_time
        
        #Check is sequence has changed
        newSequence = get_sequence(deviceName)[deviceName]
        if (sequence!=newSequence):
            sequence = newSequence
            current_index = 0
            print("New Sequence detected. Flashing yellow for 5s")
            
            flashStartTime = time.time()
            while (time.time()-flashStartTime<5):
                serialWrite("yellow")
            print("Yellow flash stopped")
        
        # Check if it's time to send the next color
        if elapsed_time >= duration:
            current_index += 1
            if current_index > 2:  # Reset to 0 after the last color
                current_index = 0
            color = sequence[str(current_index)]["color"]
            duration = sequence[str(current_index)]["time"]

            print(f"Sending {color} for {duration} seconds...")
            serialWrite(color)

            last_send_time = current_time

        # Read data from Arduino if available
        data = serialRead()
        # if data:
        #     print(f"Received: {data}")
