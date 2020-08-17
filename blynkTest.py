from picamera import PiCamera
import cv2
import time
import cvlib as cv
import BlynkLib
import datetime
import requests
import base64
from cvlib.object_detection import draw_bbox
import httplib2 as http  # External library
from urllib.parse import urlparse
import json
import math
import Adafruit_DHT

x =0

camera = PiCamera()

BLYNK_AUTH = 'Rtyir7iUZ0pA3IeQIR-zOyEH42QhuE-x'
blynk = BlynkLib.Blynk(BLYNK_AUTH)

DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 4

def weather():
    humidity, temperature = Adafruit_DHT.read_retry(DHT_SENSOR, DHT_PIN)

    if humidity is not None and temperature is not None:
        print("Temp={0:0.1f}*C  Humidity={1:0.1f}%".format(temperature, humidity))
    else:
        print("Failed to retrieve data from humidity sensor")

    temp = round(temperature,1)
    hum = round(humidity,1)
    blynk.virtual_write(3, temp)
    blynk.virtual_write(4,hum)

while True:

    now = datetime.datetime.now()

    camera.capture('/home/pi/PycharmProjects/crowdDetection/image.jpg')
    # read input image
    image = cv2.imread('image.jpg')
    # apply object detection
    bbox, label, conf = cv.detect_common_objects(image)

    output_image = draw_bbox(image, bbox, label, conf)

    cv2.imwrite("output_image.png", output_image)

    crowd = label.count('person')
    print(crowd)

    blynk.run()
    blynk.virtual_write(1, " ")

    if crowd == 0:
        status = "Empty"
        blynk.virtual_write(1, " ")
        x =0
        blynk.virtual_write(5, 1, '', '', "value")

    elif crowd >= 1:
        status = "Low crowd"

        if x == 0:
            if __name__ == "__main__":
                # Authentication parameters
                headers = {'AccountKey': 'NXpFdS3XQnqaH4jIc2g6kQ==',
                           'accept': 'application/json'}  # this is by default

                # API parameters
                uri = 'http://datamall2.mytransport.sg/'  # Resource URL
                path = 'ltaodataservice/BusArrivalv2?BusStopCode=75279'

                # Build query string & specify type of API call
            target = urlparse(uri + path)
            method = 'GET'
            body = ''

            # Get handle to http
            h = http.Http()

            # Obtain results
            response, content = h.request(target.geturl(), method, body, headers)

            # Parse JSON to print
            jsonObj = json.loads(content)

            z = len(jsonObj['Services'])

            BusService = ['', '', '', '', '']
            firstBus = ['', '', '', '', '']
            Bus1 = ['', '', '', '', '']
            BusTiming1 = ['', '', '', '', '']
            BusArr1 = ['', '', '', '', '']
            min1 = ['', '', '', '', '']
            lat = ['', '', '', '', '']
            long = ['', '', '', '', '']

            for x in range(z):
                BusService[x] = jsonObj['Services'][x]['ServiceNo']
                firstBus[x] = jsonObj['Services'][x]['NextBus']['EstimatedArrival']
                lat[x] = jsonObj['Services'][x]['NextBus']['Latitude']
                long[x] = jsonObj['Services'][x]['NextBus']['Longitude']

                Bus1[x] = (firstBus[x].replace("T", " ")).replace("+08:00", "")
                BusTiming1[x] = datetime.datetime.strptime(Bus1[x], '%Y-%m-%d %H:%M:%S')
                BusArr1[x] = ((BusTiming1[x] - now).total_seconds()) / 60
                min1[x] = math.trunc(BusArr1[x])

                print(BusService[x])
                print(min1[x])
                print("\n")

                blynk.virtual_write(1, " ")

            for x in range(z):
                if min1[x] > 10:
                    print(BusService[x])
                    blynk.notify("High Crowd! Please deploy additional bus  " + BusService[x])
                    blynk.virtual_write(1, BusService[x])
                    blynk.virtual_write(5, 1, lat[x], long[x], "value")

            blynk.notify("High Crowd, no additional deployment of buses are required")
            blynk.run()

            x = 1



    elif crowd > 15:
        status = "High crowd"
        blynk.virtual_write(1, " ")
        x =0
        blynk.virtual_write(3, 1, '', '', "value")

    print(status)

    blynk.virtual_write(0, status)
    blynk.virtual_write(2, crowd)
    blynk.run()

    weather()

