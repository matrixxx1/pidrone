# servos.py
import datetime
import RPi.GPIO as GPIO
from time import sleep

def moveServo(pinNumber, pulseWidth):
  # Pins that can do PWM = GPIO/PIN 12/32,13,18, 19
  # servo wiring = black/brown = ground.  Red = +5v, yellow = pwm
  print("moveServo - " + str(datetime.datetime.now().time()) + ", name: " + __name__ + ".moveServo(" + str(pinNumber) + "," + str(pulseWidth) + ")\n")
  GPIO.setup(pinNumber,GPIO.OUT)  # Sets up pin 11 to an output (instead of an input)
  p = GPIO.PWM(pinNumber, 50)     # Sets up pin 11 as a PWM pin
  p.start(0)               # Starts running PWM on the pin and sets it to 0
  p.ChangeDutyCycle(pulseWidth)     # Changes the pulse width to x (so moves the servo)
  sleep(1)                 # Wait 1 second  
  p.stop()                 # At the end of the program, stop the PWM
