# leds.py


def ledOn(pinNumber):
    GPIO.output(pinNumber,GPIO.HIGH)
    
def ledOff(pinNumber, duration):
    GPIO.output(pinNumber,GPIO.LOW)