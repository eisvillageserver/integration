import sync as sync
import json
import argparse
import api as app
import gsmLed as hardware
import RPi.GPIO as GPIO

onLed, syncLed, serverLed  = 22, 27 ,17
gsmNetStat, gsmPwrStat, gsmKey, gsmReset = 24, 18, 23, 25

GPIO.setmode(GPIO.BCM)
hardware.setupGSMPins(gsmNetStat, gsmPwrStat, gsmKey, gsmReset)
hardware.setupLedPins(onLed, syncLed, serverLed)
GPIO.output(onLed,True)

with open('config.json') as c:
    config = json.load(c)

cloud = sync.getCloudDatabase(config["aws"]["user"], config["aws"]["password"], config["aws"]["host"], config["aws"]["port"])
local = sync.getLocalDatabase(config["sqliteDB"])
box   = config["boxID"]

def startServer():
    GPIO.output(serverLed,True);
    app.run();
    GPIO.output(serverLed,False);

def syncData():
    try:
        hardware.preSync();
        sync.syncBoxes(box, local, cloud);
    except:
        print "Sync Error"
    hardware.postSync();

def syncFirstTime():
    sync.copyContentData(box, local, cloud);

parser = argparse.ArgumentParser()
parser.add_argument('--sync', action="store_true", help="Sync server with cloud database")
parser.add_argument('--new', action="store_true", help="Create new database and sync with cloud database. DO NOT RUN THIS WHILE CONNECTED TO THE INTERNET VIA GSM")
parser.add_argument('--run', action="store_true", help="Start the Village Server Web Application")
arg = parser.parse_args()

if arg.sync:
    syncData();

elif arg.new:
    syncFirstTime();

elif arg.run:
    startServer();

else:
    "Argument does not exist"
