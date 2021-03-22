import time
import math
import sys
from pygsm import GsmModem


def CalculateDistance(Latitude1, Longitude1, Latitude2, Longitude2):
 Latitude1 = Latitude1 * math.pi / 180
 Longitude1 = Longitude1 * math.pi / 180
 Latitude2 = Latitude2 * math.pi / 180
 Longitude2 = Longitude2 * math.pi / 180
 return 6371000 * math.acos(math.sin(Latitude2) * math.sin(Latitude1) + math.cos(Latitude2) * math.cos(Latitude1) * math.cos(Longitude2-Longitude1))

# Switch GPS on
def SwitchGPSon():
    print ("Switching GPS on ...")
    reply = gsm.command('AT+CGNSPWR=1')
    print (reply)
    print

def SwitchGPSoff():
    print ("Switching GPS off ...")
    reply = gsm.command('AT+CGNSPWR=0')
    print (reply)
    print
    
def SendGPSPosition():
    global Latitude, Longitude, Altitude
    print ("Getting GPS position ...")
    reply = gsm.command('AT+CGNSINF')
    list = reply[0].split(",")
    UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
    Latitude = list[3]
    Longitude = list[4]
    Altitude = list[5]
    print ('Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude)
    # Text to mobile
#    Message = ' Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
#    print ("Sending to mobile " + MobileNumber + ": " + Message)
#    gsm.send_sms(MobileNumber, Message)


#  DEFINE GLOBAL VARIABLES
#----------------------------------------------------------------------
SendTimeout = 5.           # Send position every x minutes regardless of movement
HorizontalDelta = 3.      # Send position if it moves horizontally by at least this many metres
VerticalDelta = 2.         # Send position if it moves vertically by at least this many metres


#  variabile logica per capire quando c'è stata una variazione di posizione
changeXYZ = 0

# Set mobile number here
MobileNumber = "+39xxxxxxxxx" #  Set here mobile number

print ("Booting modem ...")
gsm = GsmModem(port="/dev/ttyS0")
gsm.boot()

print ("Modem details:")
reply = gsm.hardware()
print ("Manufacturer = " + reply['manufacturer'])
print ("Model = " + reply['model'])

# Try and get phone number
reply = gsm.command('AT+CNUM')
if len(reply) > 1:
 list = reply[0].split(",")
 phone = list[1].strip('\"')
 print ("Phone number = " + phone)
 print

print ("Deleting old messages ...")
gsm.query("AT+CMGD=1,4")
print

SwitchGPSon()

# ricava posizione iniziale
SendGPSPosition()

PreviousAltitude = float(Altitude)
PreviousLatitude = float(Latitude)
PreviousLongitude = float(Longitude)

# ricevi la posizione iniziale sul cellulare
#Message = ' Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
#print ("Sending to mobile " + MobileNumber + ": " + Message)
#gsm.send_sms(MobileNumber, Message)

print ("Boot successful, waiting for messages ...")

while True:  
    
 # Check messages
 message = gsm.next_message()

 if message:
  print (message)
  text = message.text
  
  if text[0:5] == 'Check':
     print ("Controllo GPS...")
     SendGPSPosition()
     Message = ' Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
     print ("Sending to mobile " + MobileNumber + ": " + Message)
     gsm.send_sms(MobileNumber, Message)

     PreviousAltitude = float(Altitude)
     PreviousLatitude = float(Latitude)
     PreviousLongitude = float(Longitude) 
     time.sleep(300)
     
 else: 
  # get position info from GPS
   reply = gsm.command('AT+CGNSINF')
   list = reply[0].split(",")
   
   if len(list[2]) > 14:
     UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
     Latitude = list[3]
     Longitude = list[4]
     Altitude = list[5]
     print('Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude)
 
#  calculate horizontal distance
     Distance = abs(CalculateDistance(float(Latitude), float(Longitude), PreviousLatitude, PreviousLongitude))
     Message = ' Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)

     if Distance >= HorizontalDelta:
        SendGPSPosition()
        changeXYZ = 1    
        print ("Inviato per spostamento orizzontale al numero " + MobileNumber + ": " + Message)
#       gsm.send_sms(MobileNumber, Message)        

     if abs(float(Altitude) - PreviousAltitude) >= VerticalDelta:
        SendGPSPosition()
        changeXYZ = 1
        print ("Inviato per movimento verticale al numero " + MobileNumber + ": " + Message)
#       gsm.send_sms(MobileNumber, Message)           

     if (changeXYZ == 1):
        changeXYZ = 0
        PreviousAltitude = float(Altitude)
        PreviousLatitude = float(Latitude)
        PreviousLongitude = float(Longitude)
   time.sleep(300)
