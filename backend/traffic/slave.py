import json
import requests
import serial
import socket
import time
import threading
import math

serverIp = "http://192.168.0.187:5000"
arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)  



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

start_time = 0
elapsed_time = 0
last_send_time = 0
timeLeft = 0
deviceName = None
sequenceList = None
sequence = None
deviceIp = get_local_ip()  # Get the local IP address
deviceList = get_all_devices()  # Fetch the device list

if __name__ == "__main__":
    # Get deviceName and sequence based on IP
    sequenceList = get_all_sequences()
    for i in deviceList:
        if deviceList[i]["ip"] == deviceIp:
            deviceName = i
            sequence = sequenceList[deviceName]
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
    try:
        
        while True:
            #Manual mode
            
            
            #Auto mode
            current_time = time.time()
            elapsed_time = current_time - last_send_time
            timeLeft = math.ceil(sequence[str(current_index)]["time"] - elapsed_time)
            if timeLeft<0:
                timeLeft=0
            requests.post(serverIp + "/setState/" + deviceName, json={"color": color, "timeLeft": timeLeft}, timeout=1)
        
            #Check is sequence has changed
            sequenceList = get_all_sequences()
            newSequence = sequenceList[deviceName]
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
            #Arduino forces green
            if data=="green":
                for i in sequence:
                    if sequence[i]["color"]=="green":
                        current_index = sequence[i]
                    
    except serial.SerialException as e:
        print(f"Serial Error: {e}")
    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Exiting...")
    finally:
        # Ensure the serial connection is closed
        if arduino and arduino.is_open:
            arduino.close()
            print("Serial connection closed.")