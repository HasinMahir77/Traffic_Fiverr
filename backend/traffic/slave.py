import json
import requests
import serial
import socket
import time
import math

serverIp = "http://192.168.0.187:5000"
try:
    arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
except serial.SerialException as e:
    print(f"Error initializing serial connection: {e}")
    arduino = None  # Set to None if initialization fails


def serialWrite(data):
    try:
        if arduino and arduino.is_open:
            arduino.write(f"{data}\n".encode())
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
        print(f"Error fetching sequence {url}: {e}")
        return None


def get_public_ip():
    try:
        response = requests.get("https://api.ipify.org?format=json", timeout=5)
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

if __name__ == "__main__":
    try:
        # Initialize start
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
            device = get_device(deviceName)

            # Auto Mode
            if device["mode"] == "auto":
                current_time = time.time()
                elapsed_time = current_time - last_send_time
                timeLeft = max(0, math.ceil(sequence[str(current_index)]["time"] - elapsed_time))

                try:
                    requests.post(
                        f"{serverIp}/setState/{deviceName}",
                        json={"color": color, "timeLeft": timeLeft},
                        timeout=1,
                    )
                except requests.exceptions.RequestException as e:
                    print(f"Error posting state: {e}")

                # Read data from Arduino if available
                data = serialRead()
                if data == "green":
                    for i, seq in sequence.items():
                        if seq["color"] == "green":
                            current_index = int(i)
                            break

                # Check if sequence has changed
                sequenceList = get_all_sequences()
                newSequence = sequenceList.get(deviceName) if sequenceList else None
                if sequence and newSequence and sequence != newSequence:
                    sequence = newSequence
                    current_index = 0
                    print("New Sequence detected. Flashing yellow for 5s")

                    flashStartTime = time.time()
                    while time.time() - flashStartTime < 5:
                        serialWrite("yellow")
                    print("Yellow flash stopped")

                # Check if it's time to send the next color
                if elapsed_time >= duration:
                    current_index = (current_index + 1) % len(sequence)
                    color = sequence[str(current_index)]["color"]
                    duration = sequence[str(current_index)]["time"]

                    print(f"Sending {color} for {duration} seconds...")
                    serialWrite(color)
                    last_send_time = current_time

    except KeyboardInterrupt:
        print("\nKeyboard Interrupt: Exiting...")
    except Exception as e:
        print(f"Unexpected error: {e}")
    finally:
        if arduino and arduino.is_open:
            arduino.close()
            print("Serial connection closed.")