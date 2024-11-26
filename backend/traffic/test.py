import time
import serial
arduino = None
i= 0
def connect_serial():
    global arduino
    try:
            arduino = serial.Serial(port='COM6', baudrate=9600, timeout=0.1)
            print("Successfully reconnected to serial.")

    except serial.SerialException as e:
        print(f"Error reconnecting to serial")
def arduinoConnected():
    global arduino
    try:
        if arduino:
            arduino.readline()
            return True
    except serial.SerialException as e:
        return False
    
connect_serial()
while 1:
    if (arduinoConnected()):
        print("Connected")
    else:
        print("Disconnected. Attempting Reconnection")
        connect_serial()
    time.sleep(0.5)
    