import json
import requests
import serial
import socket
import time
import math

serverIp = "http://192.168.0.187:5000"
arduino = None  # Initialize arduino to None first

# Function to attempt reconnecting to the serial port
def connect_serial():
    global arduino
    try:
        print("Attempting to reconnect to serial port...")
        arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
        print("Successfully reconnected to serial.")
    except serial.SerialException as e:
        print(f"Error reconnecting to serial")


def serialWrite(data):
    try:
        if arduino and arduino.is_open:
            arduino.write(f"{data}\n".encode())
            print("Written to serial: "+ data)
            time.sleep(0.1)
    except serial.SerialException as e:
        print(f"Error writing to serial: {e}")


def serialRead():
    try:
        if arduino and arduino.in_waiting > 0:
            data = arduino.readline().decode().strip()
            return data
    except serial.SerialException as e:
        print(f"Error reading from serial: {e}")
def arduinoConnected():
    global arduino
    try:
        if arduino:
            arduino.readline()
            return 1
    except serial.SerialException as e:
        return 0
    


def get_all_devices():
    url = f"{serverIp}/getAllDevices/"
    try:
        response = requests.get(url, timeout=0.1)  # Added timeout
        response.raise_for_status()  # Raise an exception for HTTP errors
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all devices: {e}")
        return None


def get_all_sequences():
    url = f"{serverIp}/getAllSequences/"
    try:
        response = requests.get(url, timeout=0.1)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching all sequences: {e}")
        return None


def get_device(device_id):
    url = f"{serverIp}/getDevice/{device_id}"
    try:
        response = requests.get(url, timeout=0.1)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching device {url}: {e}")
        return None


def get_sequence(device_id):
    url = f"{serverIp}/getSequence/{device_id}"
    try:
        response = requests.get(url, timeout=0.1)  # Added timeout
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fetching sequence {url}: {e}")
        return None


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=0.1)
        return response.json()["ip"]
    except requests.exceptions.RequestException as e:
        print(f"Error fetching public IP: {e}")
        return None


def get_local_ip():
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.connect(("8.8.8.8", 80))
            return s.getsockname()[0]
    except socket.error as e:
        print(f"Error fetching local IP: {e}")
        return None


start_time = 0
elapsed_time = 0
last_send_time = 0
timeLeft = 0
deviceName = None
sequenceList = None
sequence = None
deviceIp = get_local_ip()
deviceList = get_all_devices()
device = None
mode = "auto"
sendFlag = 0
#Manual Mode vars
prevColor = 0

if __name__ == "__main__":
    try:
        # Initialize start
   
        #connect_serial()
    
    
        
        sequenceList = get_all_sequences()
        if not sequenceList or not deviceList:
            raise ValueError("Failed to fetch device or sequence list")

        for i in deviceList:
            if deviceList[i]["ip"] == deviceIp:
                deviceName = i
                device = deviceList[i]
                sequence = sequenceList[deviceName]
                print(f"Device Name: {deviceName}")
                print(f"Sequence: {sequence}")
                break

        if not deviceName:
            print("Device not found!")
            exit(1)

        current_index = 0
        last_send_time = time.time()
        color = sequence[str(current_index)]["color"]
        duration = sequence[str(current_index)]["time"]
        print(f"Sending {color} for {duration} seconds...")
        serialWrite(color)

        # Main loop
        while True:
            if (not arduinoConnected()):
                print("Arduino disconnected. Attempting reconnection.")
                connect_serial()
            device = get_device(deviceName)
            mode = deviceList[deviceName]["mode"]
            # Heartbeat
            try:
                requests.post(
                    f"{serverIp}/setLastReply/{deviceName}",
                    json={"connected": 1},
                    timeout=0.2,
                )
            except requests.exceptions.RequestException as e:
                print(f"Heartbeat error: {e}")

            # Manual Mode
            if device["mode"] == "manual":
                color = device["manualColor"]
                if color!=prevColor:
                    serialWrite(color)
                    prevColor = color
        
            # Auto Mode
            elif device["mode"] == "auto":
                current_time = time.time()
                elapsed_time = current_time - last_send_time
                timeLeft = max(0, math.ceil(sequence[str(current_index)]["time"] - elapsed_time))

                try:
                    requests.post(
                        f"{serverIp}/setState/{deviceName}",
                        json={"color": color, "timeLeft": timeLeft, "arduino":arduinoConnected()},
                        timeout=0.5,  # Increased timeout for stability
                    )
                except requests.exceptions.RequestException as e:
                    print(f"Error posting state: {e}")

                # Read data from Arduino if available and arduino is connected
                if arduino:
                    data = serialRead()
                    if data == "green":
                        for i, seq in sequence.items():
                            if seq["color"] == "green":
                                current_index = int(i)
                                break

                # Check if sequence has changed
                try:
                    sequenceList = get_all_sequences()
                    newSequence = sequenceList.get(deviceName) if sequenceList else None
                    if sequence and newSequence and sequence != newSequence:
                        sequence = newSequence
                        current_index = 0
                        print("New Sequence detected. Flashing yellow for 5s")

                        flashStartTime = time.time()
                        while time.time() - flashStartTime < 5:
                            try:
                                requests.post(
                                f"{serverIp}/setState/{deviceName}",
                                json={"color": "yellow", "timeLeft": timeLeft},
                                timeout=0.5,  # Increased timeout for stability
                                )
                                serialWrite("yellow")
                            except requests.exceptions.RequestException as e:
                                print(f"Error: {e}")
                                
                        print("Yellow flash stopped")
                except Exception as e:
                    print(f"Error checking for new sequence: {e}")

                # Check if it's time to send the next color
                try:
                    if elapsed_time >= duration:
                        current_index = (current_index + 1) % len(sequence)
                        color = sequence[str(current_index)]["color"]
                        duration = sequence[str(current_index)]["time"]

                        
                        if arduino:  # Only attempt serialWrite if arduino is initialized
                            print(f"Sending {color} for {duration} seconds...")
                            serialWrite(str(color))
                        last_send_time = current_time
                except Exception as e:
                    print(f"Error checking or sending next color: {e.with_traceback}")

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
            
                
            
