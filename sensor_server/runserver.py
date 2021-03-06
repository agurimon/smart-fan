from flask import Flask, redirect, url_for, request, jsonify
import requests
import RPi.GPIO as gpio
import time

app = Flask(__name__)

gpio.setmode(gpio.BCM)
gpio.setwarnings(False)

trig = [5, 20, 23, 17, 4, 12, 26]
echo = [6, 21, 24, 18, 22, 13, 27]

for i in range(7):
    gpio.setup(trig[i], gpio.OUT)
    gpio.setup(echo[i], gpio.IN)


def observation(trig, echo):
    gpio.output(trig, False)
    time.sleep(0.5)
    gpio.output(trig, True)
    time.sleep(0.00001)
    gpio.output(trig, False)
   
    pulse_start = 0
    pluse_end = 0
    
    while gpio.input(echo) == 0:
        pulse_start = time.time()

    while gpio.input(echo) == 1:
        pulse_end = time.time()
    
    pulse_duration = pulse_end - pulse_start
    
    distance = pulse_duration*17000
    distance = round(distance,2)
    
    return distance


def range_check(sensors, human_location):            
    for i in range(7):
        if sensors[i] != 0:
            human_location[i] = 1

    temp = []
    num = 6

    while True:
        if num == -1:
            break

        temp.append(human_location[num])
        num -= 1
    
    return temp
        
    
def find_left(li):
    for i in range(7):
        if li[i] == 1:
            return i
    return 0

        
def find_right(li):
    for i in range(6,-1,-1):
        if li[i] == 1:
            return i
    return 0


@app.route('/sensing')
def sensing():   
    ip_addr = 'http://' + request.remote_addr + ':8080/sensor/enroll'
    
    left = 0
    right = 0
    sensors=[0, 0, 0, 0, 0, 0, 0]
    human_location=[0, 0, 0, 0, 0, 0, 0]

    for i in range(7):
        sensors[i] = observation(trig[i], echo[i])

        if sensors[i] > 60:
            sensors[i] = 0
        
        print(sensors[i])

    human_location = range_check(sensors, human_location)
    
    left = find_left(human_location)
    right = find_right(human_location)
    data = {'left': left, 'right': right}

    res = requests.post(ip_addr, data=data)
    
    return '이정윤 천재'


@app.route('/')
def index():
    return 'hello, sensor server!'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080)
