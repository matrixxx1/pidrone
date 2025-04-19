# motor.py
class motor:
    def __init__(self, setPin, setSpeed):
        self.pin = setPin
        self.speed = setSpeed
        GPIO.setup(setPin,GPIO.OUT)
        self.pinControl = GPIO.PWM(setPin, 50)
        self.pinControl.start(0)
        self.pinControl.ChangeDutyCycle(setSpeed)
        
    def setSpeed(newSpeed):
        self.speed = newSpeed