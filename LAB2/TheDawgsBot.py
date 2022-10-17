from utils.brick import Motor
from time import sleep


def motorConfig(portLeft, portRight):
    motorLeft = Motor(portLeft)
    motorRight = Motor(portRight)

    motorLeft.set_position(0)
    motorRight.set_position(0)
    sleep(5)
    motorLeft.set_power(0)
    motorRight.set_power(0)
    print("Motors Ready.")
    return [motorLeft,motorRight]

def convertToRelativePosition(absolutePosition):
    if absolutePosition < 90:
        return 0
    return 1

def drums(relativePosition, motors):
    if relativePosition == 0:
        # turn off drums
        motors[1].set_power(0)
        motorPositions[0] = 0
    elif relativePosition == 1:
        #play something
        motors[1].set_power(30)
        motorPositions[0] = 1

def main ():
    
    motors = motorConfig("C","B")
    global motorPositions
    motorPositions  = [0,0]
    
    
    while True:
        print(motorPositions[0])
        if convertToRelativePosition(motors[0].get_position()) != motorPositions[0]:
            drums(convertToRelativePosition(motors[0].get_position()),motors)
            
        sleep(1)
    
    
main()