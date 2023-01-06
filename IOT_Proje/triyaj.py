import RPi.GPIO as GPIO
import time
import datetime
from smbus2 import SMBus
from mlx90614 import MLX90614
from pirc522 import RFID
import signal
import max30102
import hrcalc
import sys
import os
from pyrebase import pyrebase
GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

m = max30102.MAX30102()
#firebase connection
config = {
  "apiKey": "AIzaSyC-P_rbMsg8I__GivHxcDKu_AK7bUXTTSM",
  "authDomain": "iot-triyaj.firebaseapp.com",
  "databaseURL": 	"https://iot-triyaj-default-rtdb.firebaseio.com",
  "storageBucket": "iot-triyaj.appspot.com"
}
firebase = pyrebase.initialize_app(config)
db = firebase.database()
GPIO_TRIGGER = 29
GPIO_ECHO= 31
ledk = 36
leds = 38
ledy = 40
buzzer = 37
rdr = RFID()
util = rdr.util()
util.debug = True
GPIO.setup(GPIO_TRIGGER,GPIO.OUT)
GPIO.setup(GPIO_ECHO,GPIO.IN)
GPIO.setmode(GPIO.BOARD)
GPIO.setup(ledk, GPIO.OUT)
GPIO.setup(leds, GPIO.OUT)
GPIO.setup(ledy, GPIO.OUT)
GPIO.setup(buzzer, GPIO.OUT)
sirano = 0
os.system("espeak 'welcome, please read your card'")
def distance():
    # set Trigger to HIGH
    GPIO.output(GPIO_TRIGGER, True)
 
    # set Trigger after 0.01ms to LOW
    time.sleep(0.00001)
    GPIO.output(GPIO_TRIGGER, False)
 
    StartTime = time.time()
    StopTime = time.time()
 
    # save StartTime
    while GPIO.input(GPIO_ECHO) == 0:
        StartTime = time.time()
 
    # save time of arrival
    while GPIO.input(GPIO_ECHO) == 1:
        StopTime = time.time()
 
    # time difference between start and arrival
    TimeElapsed = StopTime - StartTime
    # multiply with the sonic speed (34300 cm/s)
    # and divide by 2, because there and back
    distance = (TimeElapsed * 34300) / 2
 
    return distance
def sicaklik():
    bus = SMBus(1)
    sensor = MLX90614(bus, address=0x5A)
 
    sicaklik = sensor.get_object_1()
    bus.close()
    return sicaklik
def kart():
   # rdr.wait_for_tag()
    time.sleep(1.5)
    (error, data) = rdr.request()
    if not error:
     (error, uid) = rdr.anticoll()
    if not error:
  # Print UID
     kart_uid = str(uid[0])+" "+str(uid[1])+" "+str(uid[2])+" "+str(uid[3])+" "+str(uid[4])
      
     return kart_uid
def nabiz():
    time.sleep(2)
    red, ir = m.read_sequential()
    
    hr,hrb,sp,spb = hrcalc.calc_hr_and_spo2(ir, red)
    if(hrb == True and hr < 150):
        hr2 = int(hr)
        
  
        return hr2     

if __name__ == '__main__':
    try:
        while True:
           
            kar = kart()
            if kar == None:
             continue
            else:
             print("kart no",kar)
             GPIO.output(ledk, True)
             GPIO.output(buzzer, True)
             time.sleep(0.5)
             GPIO.output(ledk, False)
             GPIO.output(buzzer, False)
             sirano = sirano+1
             print("Sira No",sirano)
             tarih = str(datetime.datetime.now())
             print("Tarih",tarih)
             dato = {"kimlik":(kar),"sira":(sirano),"tarih":(tarih)}
             db.child("Hasta_Verileri").update(dato)
             nab = nabiz()
             if nab != None:
              print("Heart Rate : ",nab)
              dato = {"nabiz":(nab)}
              db.child("Hasta_Verileri").update(dato)
              GPIO.output(leds, True)
              time.sleep(0.5)
              GPIO.output(leds, False)
              
              dist = distance()
            
              sic = sicaklik()
              if 1 < dist < 15:
               print("sicaklik",sic)
               GPIO.output(ledy, True)
               time.sleep(0.5)
               GPIO.output(ledy, False)
               dato = {"sicaklik":(sic)}
               db.child("Hasta_Verileri").update(dato)
               continue
              time.sleep(1)
 
        # Reset by pressing CTRL + C
    except KeyboardInterrupt:
        print("Measurement stopped by User")
        GPIO.cleanup()
