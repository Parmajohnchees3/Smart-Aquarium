import serial
import time
import requests

from w1thermsensor import W1ThermSensor
sensor = W1ThermSensor()

# Define the URL endpoint to send the POST request to
url = 'http://18.221.200.217:5000/receive_data'


# Initialize serial communication
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.reset_input_buffer()

while True:

    # Read temperature sensor
    temperature = sensor.get_temperature()
    print("The temperature is %s celsius" % temperature)
    try:
        float_temp = float(temperature)
    except ValueError:
        print("Invalid float representation")
        continue

    # Read pH value via UART communication
    if ser.in_waiting > 0:
        pH = ser.readline().decode('utf-8').rstrip()
        print("The pH is %s" % pH)
    else:
        pH = "error"

    try:
        float_ph = float(pH)
    except ValueError:
        print("Invalid float representation")
        continue


    # Define the data to be sent in the POST request (as a dictionary)
    data = {'temp': float_temp, 'ph': float_ph }
    headers = {'Content-Type': 'application/json'}  # JSON content type

    # Send the POST request with the defined URL and data
    response = requests.post(url, json=data, headers=headers)

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        print('POST request successful!')
        print('Response:', response.text)
    else:
        print('POST request failed:', response.status_code)

    time.sleep(5)