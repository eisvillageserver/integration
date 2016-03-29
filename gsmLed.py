import RPi.GPIO as GPIO
import sys
import time
import os
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

#Check if gsm is on or off
#Input is high if ON, low if OFF
def isPwrOnGSM(pwrStat):
    return GPIO.input(pwrStat)

#Switch from on to off or off to on
#To switch GSM on/off, pull key down for 2 seconds
def switchPwrStatGSM(key):
    GPIO.output(key, GPIO.LOW)
    sleep(3)
    GPIO.output(key,GPIO.HIGH)
    return True

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

#set brightness on scale of 0-100, software pwn used to dim the Led
def setLedBrightness(brightness,LedPin):
    PWM = GPIO.PWN(LedPin,100)
    PWM.start(brightness)
    return True
