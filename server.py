# Server.py

# Runs Aurdino
# Sends data from an HTTP get request

# Server and Data
from http.server import BaseHTTPRequestHandler, HTTPServer
import json

# Serial Port
import pyfirmata

# Threading
import threading
import time

# Data - Not used here but will make life easier when dealing with datasets
import pandas as pd
import numpy as np

# Image for the Color Ramp
from PIL import Image

# Data we loop through with the buttonns
cities  = ["Boston","New York","Los Angeles","Chicago","Miami","Anchorage","Hilo","Honolulu","Phoenix","Oregon","Vancouver"]
seasons = ["Winter","Spring","Summer","Fall"]

# Variables changed by the inputs
city = 0
year = 1960
season = 0

#Additional Data to track
prcp = 0
temp = 0
colrs = [];

# Server Class 
class S(BaseHTTPRequestHandler):

    # Sets the headers for the response. 
    # We're sending json data
    # Access-Control-Allow-Orgin let's us work from anywhere. 
    # This isn't safe, but works for the project
    def _set_response(self):
        self.send_response(200)
        self.send_header('Content-type','application/json')
        self.send_header('Access-Control-Allow-Origin','*')
        self.end_headers()
    
    # Get Request
    # We set the response
    # Convert a dictonary into json, in this case a dictonary containing the button int
    # Sends it out
    def do_GET(self):
        self._set_response()

        json_str = json.dumps({"city":[cities[city]],"year":[year],"season":[seasons[season]],"temp":[int(temp)],"prcp":[int(prcp)],"color":[colrs]})
        self.wfile.write(json_str.encode(encoding='utf_8'))

# Runs the server
def run(server_class=HTTPServer,handler_class=S,port=3000):
    # Gets teh adddress and sets that up
    server_address = ('',port)
    httpd = server_class(server_address,handler_class)

    print(f"Serving at port http://localhost:{port}")

    # Runs the server forvver until  you hit ctrl-c
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    httpd.server_close()

#Gets color based on the tempature reading
def getScaleColor(tmp):
    if(tmp<0):
        tmp=0
    if(tmp>100):
        tmp=100
    tmp = int(tmp)

    # Pulls from a color scale and sends that to the LED/Display
    global colrs
    colrs = Image.open("colorRamp.png").convert("RGB").getpixel((tmp,0))
    
    return (colrs[0],colrs[1]/2,colrs[2])

def getAOutputs(w):
    # Gets a single row of the weather season data
    snapWeather = w.loc[(cities[city],year,seasons[season])]

    # Gets the two variables
    p = float(snapWeather["sumPrcp"])
    tmp = float(snapWeather["temp"])
    
    # Sends that to global variables
    global prcp
    global temp
    temp = tmp 
    prcp = p
    pumpRate = 0

    #Sets the pumprate based on the percipitation
    if(p>20):
        pumpRate = 1
    elif (p>12):
        pumpRate = .9
    elif (p>6):
        pumpRate = .8
    elif (p > 2.5):
        pumpRate=.7
    elif(p>0.5):
        pumpRate=.6
    else:
        pumpRate = 0

    return pumpRate, getScaleColor(tmp)

# Previous light color function
def lightColor(w):
    tem = w.loc[(cities[city],year,seasons[season])]

# Thread 1: Does the server stuff
def server():
    run()

# Thread 2: Does the arduino stuff
# This is a simple function that checks if the button at pin 2 is being pressed
def ardunio(buttonOne,buttonTwo,knob,pump,w,lights):
    print("Starting")

    boHasPressed = False
    btHasPressed = False
    while(True):
        # Reads the input pins
        bo = buttonOne.read()
        bt = buttonTwo.read()
        k = knob.read()

        # If city button is on
        if bo is True and boHasPressed is False:
            global city
            city += 1
            city = city%11
            boHasPressed = True

        #If season button is on
        if bt is True and btHasPressed is False:
            global season
            season += 1
            season = season%4
            btHasPressed = True

        # Makes it so one push = one change
        if bo is False and boHasPressed is True:
            boHasPressed = False
        
        if bt is False and btHasPressed is True:
            btHasPressed = False
        
        # Sets teh year value
        global year
        year = int(59 * k) + 1960

        #Gets pump rate and LED color
        pumpRate,colors = getAOutputs(w)

        #Send pump rate to pumpo
        pump.write(pumpRate)
        
        #Sends color to LED
        for i in range(0,3):
            lights[i].write(colors[i]/256)
        time.sleep(0.1)

# Main function
if __name__ == '__main__':
    from sys import argv

    # Setting up the board, 
    # Use whatever serial port you are plugged into (what you choose in Arudino)
    board = pyfirmata.Arduino('/dev/cu.usbserial-14510')
    it = pyfirmata.util.Iterator(board)
    it.start()

    # Getting all the pins we need
    buttonOne = board.get_pin('d:7:i')
    buttonTwo = board.get_pin('d:6:i')
    knob = board.get_pin('a:0:i')
    pump = board.get_pin('d:3:p')

    lightGreen = board.get_pin('d:11:p')
    lightBlue = board.get_pin('d:10:p')
    lightRed = board.get_pin('d:9:p')

    lights = [lightRed,lightGreen,lightBlue]

    #Getting our weather data
    weather = pd.read_csv("Data/seasonalWeather.csv").set_index(["CommonName","year","season"]).sort_index()


    # Sets up the threading, one for the server and one for the ardunio 
    t = threading.Thread(name='server', target=server)
    w = threading.Thread(name='ardunio', target=ardunio,args=[buttonOne,buttonTwo,knob,pump,weather,lights])
    w.start()
    if len(argv) == 2:
        run(port=int(argv[1]))
    else:
        t.start()

