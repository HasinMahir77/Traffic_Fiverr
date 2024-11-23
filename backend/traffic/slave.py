import requests
import serial
import socket
import time
import flask

serverIp = "http://192.168.0.236:5000"
#arduino = serial.Serial(port='COM3', baudrate=9600, timeout=0.1)  

def send_to_arduino(data):
    arduino.write(f"{data}\n".encode())  
    time.sleep(0.1)  
    
def receive_from_arduino():
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
    url = f"{serverIp}/getDevice/{url}"
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
  
if __name__ == "__main__":
    deviceName = 0
    sequence = 0
    deviceIp = get_local_ip()
    deviceList = get_all_devices()
    sequenceList = get_all_sequences()
    
    #Get deviceName
    for i in deviceList:
        if deviceList[i]["ip"]==deviceIp:
            deviceName = i
            sequence = sequenceList[deviceName]
            print(deviceName)
            print(sequence)
    
    
    
    