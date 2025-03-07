# flight.py



def moveForward():
    frontLeft.setSpeed(frontLeft.speed - 100)
    frontRight.setSpeed(frontLeft.speed - 100)
    backLeft.setSpeed(frontLeft.speed + 100)
    backRight.setSpeed(frontLeft.speed + 100)
    
def moveBackward():
    frontLeft.setSpeed(frontLeft.speed + 100)
    frontRight.setSpeed(frontLeft.speed + 100)
    backLeft.setSpeed(frontLeft.speed - 100)
    backRight.setSpeed(frontLeft.speed - 100)

def moveLeft():
    frontLeft.setSpeed(frontLeft.speed - 100)
    frontRight.setSpeed(frontLeft.speed + 100)
    backLeft.setSpeed(frontLeft.speed - 100)
    backRight.setSpeed(frontLeft.speed + 100)
    
def moveRight():
    frontLeft.setSpeed(frontLeft.speed + 100)
    frontRight.setSpeed(frontLeft.speed - 100)
    backLeft.setSpeed(frontLeft.speed + 100)
    backRight.setSpeed(frontLeft.speed - 100)

def moveUp():
    frontLeft.setSpeed(frontLeft.speed + 100)
    frontRight.setSpeed(frontLeft.speed + 100)
    backLeft.setSpeed(frontLeft.speed + 100)
    backRight.setSpeed(frontLeft.speed + 100)

def moveDown():
    frontLeft.setSpeed(frontLeft.speed - 100)
    frontRight.setSpeed(frontLeft.speed - 100)
    backLeft.setSpeed(frontLeft.speed - 100)
    backRight.setSpeed(frontLeft.speed - 100)
