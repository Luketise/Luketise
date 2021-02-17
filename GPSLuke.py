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

SendTimeout = 5			# Send position every x minutes regardless of movement
HorizontalDelta = 15	# Send position if it moves horizontally by at least this many metres
VerticalDelta = 2		# Send position if it moves vertically by at least this many metres
MaxGSMAltitude = 2000	# Don't try to send above this altitude

PreviousSeconds = 0
PreviousAltitude = 0
PreviousLatitude = 0
PreviousLongitude = 0

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
    print ("Getting GPS position ...")
    reply = gsm.command('AT+CGNSINF')
    list = reply[0].split(",")
    UTC = list[2][8:10]+':'+list[2][10:12]+':'+list[2][12:14]
    Latitude = list[3]
    Longitude = list[4]
    Altitude = list[5]
    print ('Position: ' + UTC + ', ' + Latitude + ', ' + Longitude + ', ' + Altitude)
    # Text to mobile
    Message = ' Position: ' + UTC + ', ' + str(Latitude) + ', ' + str(Longitude) + ', ' + str(Altitude) + ' http://maps.google.com/?q=' + str(Latitude) + ',' + str(Longitude)
    print ("Sending to mobile " + MobileNumber + ": " + Message)
    gsm.send_sms(MobileNumber, Message)


# Set mobile number here
MobileNumber = "+393480348015"
lastmessage = 'Stop'

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

print ("Boot successful, waiting for messages ...")

while True:
        
    Distance = abs(CalculateDistance(Latitude, Longitude, PreviousLatitude, PreviousLongitude))
    if Distance >= HorizontalDelta:
     SendGPSPosition () 
     print("Inviato per movimento orizzontale")

    if abs(Altitude - PreviousAltitude) >= VerticalDelta:
     SendGPSPosition () 
     print("Inviato per spostamento verticale")    
        
    if SendGPSPosition:
       PreviousAltitude = Altitude
       PreviousLatitude = Latitude
       PreviousLongitude = Longitude
        
    # Check messages
    message = gsm.next_message()

    if message:
     print (message)
     text = message.text
     if text[0:5] == 'Check':
      print ("Start sending Position ...")
      SendGPSPosition()
      lastmessage = 'Stop'
      time.sleep(300)
