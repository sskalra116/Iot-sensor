from coapthon.server.coap import CoAP
from exampleresources import BasicResource
from coapthon.resources.resource import Resource

import os  
import glob  
import time
import RPi.GPIO as GPIO
from time import sleep

LEDPin1 = 17
i =0

os.system('modprobe w1-gpio')  
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'  
device_folder = glob.glob(base_dir + '28*')[0]  
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    
    f = open(device_file, 'r')  
    lines = f.readlines()  
    f.close()  
    return lines

def read_temp():  
    lines = read_temp_raw()
    
    while lines[0].strip()[-3:] != 'YES':  
        time.sleep(0.2)  
        lines = read_temp_raw()  
    equals_pos = lines[1].find('t=')  
    if equals_pos != -1:  
        temp_string = lines[1][equals_pos+2:]

        #Converting the string t to float
        #And dividing the 5 digit value by 1000
        C = float(temp_string) / 1000.0  
        F = C * 9.0 / 5.0 + 32.0  
        return F


temperature = str(read_temp())
print(temperature)

class TempSensor(Resource):
    def __init__(self, name="TempSensor", coap_server=None):
        super(TempSensor, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = temperature

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = TempSensor()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True

class HelloWorld(Resource):
    def __init__(self, name="HelloWorld", coap_server=None):
        super(HelloWorld, self).__init__(name, coap_server, visible=True, observable=True, allow_children=True)
        self.payload = "Hello World"

    def render_GET(self, request):
        return self

    def render_PUT(self, request):
        self.payload = request.payload
        return self

    def render_POST(self, request):
        res = HelloWorld()
        res.location_query = request.uri_query
        res.payload = request.payload
        return res

    def render_DELETE(self, request):
        return True


class CoAPServer(CoAP):
    def __init__(self, host, port):
        CoAP.__init__(self, (host, port))
        
        self.add_resource('Hello World!/', HelloWorld())
        self.add_resource('temp/', TempSensor())

def main():
    server = CoAPServer("149.159.225.134", 5683)
    print("running")
    try:
        server.listen(10)
        
    except KeyboardInterrupt:
        print ("Server Shutdown")
        server.close()
        print ("Exiting...")

if __name__ == '__main__':
    main()
