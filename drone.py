# if pip isnt setup, run this:
# sudo apt-get install python-pip

import RPi.GPIO as GPIO  # Imports the standard Raspberry Pi GPIO library
# if not working, install this
#  pip freeze | grep RPi
# pip install RPi.GPIO


from time import sleep   # Imports sleep (aka wait or pause) into the program
import threading
import datetime
from enum import Enum
# import gpsd              # sudo apt-get install gpsd gpsd-clients

# server.py
from http.server import BaseHTTPRequestHandler, HTTPServer
import socket
import urllib.parse

import camera
import motor
import flight
import leds
import hardware_servos
from picamera2 import Picamera2
from time import sleep
import shutil
from PIL import Image, ImageDraw, ImageFont

serverRunning=True

picam2 = Picamera2()


camera_config = picam2.create_still_configuration(main={"size": (1920, 1080)}, lores={"size": (640, 480)}, display="lores")
picam2.configure(camera_config)

maxRange = 180
servoFreq = 50


class world:
  def __init__(self):
    self.x=[0,0,0,0,0,0,0,0,0,0]
    self.y=[0,0,0,0,0,0,0,0,0,0]
    self.z=[0,0,0,0,0,0,0,0,0,0]



def getPWMByAngle(angle):
    return int(((angle / maxRange) * (10 +2) + 0) ) 
    #return (desiredAngle / maxDegrees) * (MaxPWM - MinPWM) + 0 = newPWM
    # return (angle / 180) * (10 + 2)  # Calculate duty cycle based on angle

 
def shutDown():
    frontCamera.stop()       
    print("end app")
    GPIO.cleanup()           # Resets the GPIO pins back to defaults#
    serverRunning=False
    exit

    
    
GPIO.setmode(GPIO.BOARD) # Sets the pin numbering system to use the physical layout
GPIO.setup(32,GPIO.OUT) #configure pin 32 for servo control


GPIO.setup(31,GPIO.OUT) #configure pin 31 for Front left motor

motorFL = GPIO.PWM(31,50)
motorFL.start(0)
sleep(10)
motorFL.ChangeDutyCycle(3)

frontCamera = GPIO.PWM(32, 50) #set pin32 to webcam tilt control


def motor1(newAngle):    
    newPWM = getPWMByAngle(int(newAngle))
    motorFL.start(0)               # Starts running PWM on the pin and sets it to 0
    sleep(2)
    motorFL.ChangeDutyCycle(newPWM)
    sleep(2)
    motorFL.stop()

def tiltFrontCam(newAngle):    
    newPWM = getPWMByAngle(int(newAngle))
    frontCamera.start(0)               # Starts running PWM on the pin and sets it to 0
    sleep(1)
    frontCamera.ChangeDutyCycle(newPWM)
    sleep(1.5)
    frontCamera.stop()
    
def SnapFrontCam():
    destFile="cam/test.jpg"
    #picam2.start_preview(Preview.QTGL)
    picam2.start()
    picam2.capture_file(destFile)
    #picam2.stop_preview()
    picam2.stop()
    return destFile

def drawOnImage(fileName, xPos, yPos, theText):
    img = Image.open(fileName) # Open the image
    draw = ImageDraw.Draw(img) # Create a drawing object
   # font = ImageFont.truetype("arial.ttf", 22)  # Replace with your desired font
    position = (xPos,yPos)  # (x, y) coordinates
    draw.text(position, theText, fill=(255, 255, 255))  # Fill color is white, # Draw the text
    #draw.text(position, theText, font=font, fill=(255, 255, 255))  # Fill color is white, # Draw the text
    img.save(fileName) # Save the image

def getDebug():
    now = datetime.datetime.now()
    return "Still from " + now.strftime("%Y-%m-%d %H:%M:%S") + ""

# Define a custom request handler class
class MyRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        # Set the response status code
        self.send_response(200)

        # Set the headers to tell the browser the response is HTML
        
        
        parsed_path = urllib.parse.urlparse(self.path)
        query_string = parsed_path.query
         
        # Parse the query string into a dictionary
        query_params = urllib.parse.parse_qs(query_string)
        
        
        #get custom html
        with open('html/menu.html', 'r') as file:
            html_content = file.read()
    
      
        
        action = query_params.get('action',[''])[0]
        value1 = query_params.get('value',[''])[0]
        value2 = query_params.get('value2',[''])[0]
        value3 = query_params.get('value3',[''])[0]
        value4 = query_params.get('value4',[''])[0]
        value5 = query_params.get('value5',[''])[0]
        
        showVals = ""
       
        doMenu=""
         
        match action:
            case "":
                #do nothing
                print("Blank action")
                doMenu="yes"
            case "GetImage":
                print("GetImage")
                getImage=SnapFrontCam()
                drawOnImage(getImage, 10, 20, getDebug())
                #showVals = "<img id='frontcam' width='1000' height='800' src='?action=GetImage&value=" + getImage + "'>"
                self.send_response(200)
                self.send_header('Content-type', 'image/jpeg')
                self.end_headers()
                with open(getImage, 'rb') as content:
                    shutil.copyfileobj(content, self.wfile)
                doMenu="no"
            case "GetMap":
                print("GetMap")
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers() 
                #with open('map.text', 'r') as file:
                #    map_content = file.read()
                map_content = "thi is the MAP - test"
                #map_content.replace(" ","&nbsp;")
                #map_content.replace("\n","<BR>")
                self.wfile.write(map_content.encode('utf-8'))
                self.end_headers()
                doMenu="no"
            case "Shutdown":
                print("ShutDown")
                serverRunning=False
                shutDown()
                doMenu="yes"
            case "TiltFrontCam":
                print("TiltFrontCam")
                tiltFrontCam(int(value1))
                doMenu="yes"
            case "Motor1":
                print("Motor1")
                motor1(int(value1))
                doMenu="yes"
            case _:
                print("Unhandled action")
                doMenu="yes"
          
        if (doMenu=="yes"):
            self.send_header('Content-type', 'text/html')
            self.end_headers()  
            showVals = showVals + '<BR>Action=' + action + " (Value1=" + value1 + ", Value2=" +  value2 + ", Value3=" +  value3 + ", Value4=" +  value4  + ", Value5=" +  value5 + ")<BR>"
            showVals = showVals + '<BR><img id="frontcam" width="1400" height="800" src="?action=GetImage" onload="refreshCam()" />'
            showVals = showVals + '<BR><iframe id="map" width="800" height="300" src="?action=GetMap" onload="refreshMap()"></iframe>'
            html_content = html_content.replace("%showVals%", showVals)
            self.wfile.write(html_content.encode('utf-8'))


def get_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.settimeout(0)
    try:
        # doesn't even have to be reachable
        s.connect(('10.254.254.254', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


# Set up and start the HTTP server
def runserver(server_class=HTTPServer, handler_class=MyRequestHandler, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print("Starting server on http://" + get_ip() + ":" + str(port) )
    httpd.serve_forever()
 

#runserver()


def webserver():
  print("Server ip: http://" + get_ip() + ":8000")
  runserver()

if __name__ == '__main__':
    t1 = threading.Thread(target=webserver)
    t1.start()
    t1.join()
    
    

print ("Starting control loop")
loopCount=0
while serverRunning==True:
    loopCount = loopCount + 1
    print("Loop: " + str(loopCount) )
    sleep(2)

shutDown()


