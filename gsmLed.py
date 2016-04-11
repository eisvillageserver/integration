import RPi.GPIO as GPIO
import sys
import time
import os
import subprocess
#Use BCM setup for RASPI
#Recommended pinout (compatible with ALL raspi verisons)
#Led1=22, Led2=27, Led3=17
#gsmNetStat=24, gsmPwrStat=18, gsmKey=23, gsmReset=25

#initialize gsm pins
def setupGSMPins(netStat, pwrStat, key, reset):
    GPIO.setup(netStat, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(pwrStat, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    GPIO.setup(key, GPIO.OUT, initial=1)
    GPIO.setup(reset, GPIO.OUT, initial=1)
    return True

#Change the power state of the gsm. state: 0 OFF, 1 ON
def pwrStateGSM(key, pwrStat, state):
    GPIO.output(key,GPIO.HIGH)
    GPIO.output(key,GPIO.LOW)
    while (GPIO.input(pwrStat) != state):
        pass
    GPIO.output(key,GPIO.HIGH)

#Reset gsm if caught in bad state
#To hard reset, pull reset pin low for 100ms
def resetGSM(reset):
    GPIO.output(reset,GPIO.LOW)
    sleep(0.2)
    GPIO.output(reset,GPIO.HIGH)
    return True

#Initialize Led pins, set all led to be turned off initially
def setupLedPins(Led1Pin, Led2Pin, Led3Pin):
    GPIO.setup(Led1Pin, GPIO.OUT, initial=0)
    GPIO.setup(Led2Pin, GPIO.OUT, initial=0)
    GPIO.setup(Led3Pin, GPIO.OUT, initial=0)
    return True

def preSync():
    GPIO.output(syncLed,True)
    hardware.pwrStateGSM(gsmKey, gsmPwrStat, 1); #Switch GSM on
    subprocess.call("sudo service ntp restart", shell=True); #Sync Time,see S3 request time too skewed

def postSync():
    hardware.pwrStateGSM(gsmKey, gsmPwrStat, 0); #switch GSM OFF
    GPIO.output(syncLed,False);
