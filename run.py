import sync as sync
import json
import argparse
import api as app
import gsmLed as hardware
import RPi.GPIO as GPIO
import subprocess
import os.path
import time

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

def preSync():
    GPIO.output(syncLed,True)
    hardware.pwrStateGSM(gsmKey, gsmPwrStat, 1); #Switch GSM on
    subprocess.call("sudo service ntp restart", shell=True); #Sync Time,see S3 request time too skewed

def postSync():
    hardware.pwrStateGSM(gsmKey, gsmPwrStat, 0); #switch GSM OFF
    GPIO.output(syncLed,False);

def startServer():
    GPIO.output(serverLed,True);
    app.run();
    GPIO.output(serverLed,False);

def syncData():
    try:
        preSync();
        sync.syncBoxes(box, local, cloud);
        postSync();
    except:
        postSync();

def syncFirstTime():
    try:
        preSync();
        sync.copyContentData(box, local, cloud);
        postSync();
    except:
        postSync();

parser = argparse.ArgumentParser()
parser.add_argument('--sync', action="store_true", help="Sync server with cloud database")
parser.add_argument('--new', action="store_true", help="Create new database and sync with cloud database")
parser.add_argument('--run', action="store_true", help="Start the Village Server Web Application")
parser.add_argument('--load', action="store_true", help="Sync and then Start the Server")
arg = parser.parse_args()

if arg.sync:
    syncData();

elif arg.new:
    syncFirstTime();

elif arg.run:
    startServer();

elif arg.load:
    if os.path.isfile("eisvsfiles.db"):
        syncData();
    elif os.path.isfile("eisvsfiles.db"):
        syncFirstTime();
    startServer();

else:
    "Argument does not exist"
