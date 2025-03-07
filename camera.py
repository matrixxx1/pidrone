# camera.py


class camera:
    def __init__(self, setPin, newAngle):
        self.pin = setPin
        self.angle = newAngle
        servo.moveServo(self.pin, newAngle)
  
    def takePicture(self, x):
        print("Picture taken")
        
    def cameraAngle(self, newAngle):
        print("Camera Up")
        moveServo(self.pin, newAngle)

    def cameraUp(self, newAngle):
        print("Camera Up")
        cameraAngle(self.angle + newAngle)

    def cameraDown(self, newAngle):
        print("Camera Down")
        cameraAngle(self.angle - newAngle)
