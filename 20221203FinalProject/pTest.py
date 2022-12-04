# // MODULE IMPORTS

from utils.brick import Motor, reset_brick, TouchSensor, wait_ready_sensors, EV3ColorSensor
from time import sleep
import simpleaudio as s



# // CONSTANTS DECLARATION

testMode = True
SAMPLES_FOLDER = "/home/pi/ecse211/FinalProject/Samples/"
beeps = [s.WaveObject.from_wave_file(SAMPLES_FOLDER+"SimpleBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"LongBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"DoubleBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"TripleBeep.wav")]
motors = ((Motor("C"),Motor("B")),(Motor("A"),Motor("D")))
centerCubeOffset = 1.25
armOffset = 7.35
topArmOffset = 1
angleRatioCoefficient = 360/13.15
extraRewind = 20
powerVal = 100
sleepTime = -0.016*powerVal + 2.5

# // FUNCTIONS

def playBeep(beepIndex):
    beep = beeps[beepIndex]
    beepObj = beep.play()


def userInput(testMode:bool) -> list[list[int],list[int],list[int],list[int],list[int]]:
    
    userInput = [[],[],[],[],[]]
    
    if testMode:

        print("Please enter binary input:")
        for i in range(0,5):
            for j in range(0,5):
                uInput = input(f"[{i},{j}] > ")
                if (uInput == "exit"):
                    exit()
                while uInput not in ["0","1"]:
                    print("input was not binary, try again:")
                    uInput = input(f"[{i},{j}] > ")
                userInput[i].append(int(uInput))
    else:
            
        touchSensors = [TouchSensor(3),TouchSensor(4),TouchSensor(2)]
        wait_ready_sensors()
            
        for i in range(0,5):
            for j in range(0,5):
                binInput = 0 #0 by default
                takingInput = True
                    
                while takingInput:
                    
                    if touchSensors[0].is_pressed():
                        print("pressed - 0")
                        binInput = 0
                        playBeep(0)

                                
                    elif touchSensors[1].is_pressed():
                        print("pressed - 1")
                        binInput = 1
                        playBeep(0)

                    elif touchSensors[2].is_pressed():
                        print("pressed - submit")
                        playBeep(1)
                        userInput[i].append(binInput)
                        takingInput = False

                    sleep(.25)      
            #done with 1 row
            sleep(1.1)
            playBeep(2)
                
        #done with input
        sleep(1.1)
        playBeep(3)

    return userInput
        
    
def detectCubes(amount:int):
    colorSensor = EV3ColorSensor(1)
    wait_ready_sensors(True)
    initialColor = colorSensor.get_value()[3]
    errorMargin = 5
    count = amount
    while count != 0:
        currentColor = colorSensor.get_value()[3]
        if currentColor >= initialColor+errorMargin or currentColor <= initialColor - errorMargin:
            count-=1
            print(f"{amount - count} cubes loaded")
            sleep(.25)
    print(f"all cubes loaded, ready to take input")
    playBeep(1)
    

def motorConfig():
    for t in motors:
        for m in t:
            m.set_limits(power = powerVal)

def moveArmX(x:int):
    xbar = (4*x - 2) -centerCubeOffset + topArmOffset
    rotationX = angleRatioCoefficient * xbar
    motors[1][0].set_position_relative(-rotationX)
    motors[1][1].set_position_relative(-rotationX)
    sleep(sleepTime)
    motors[1][0].set_position_relative(rotationX + extraRewind)
    motors[1][1].set_position_relative(rotationX + extraRewind)
    sleep(sleepTime)

def moveArmY(y:int):
    ybar = (4*y - 2) -centerCubeOffset + armOffset
    rotationY = angleRatioCoefficient * ybar
    motors[0][0].set_position_relative(-rotationY)
    motors[0][1].set_position_relative(-rotationY)
    sleep(sleepTime)
    motors[0][0].set_position_relative(rotationY + extraRewind)
    motors[0][1].set_position_relative(rotationY + extraRewind)
    sleep(sleepTime)

# // MAIN PROGRAM

def main():
    motorConfig()
    detectCubes(10)
    uInput = [[1,0,0,0,1],[0,1,0,1,0],[0,0,1,0,0],[0,1,0,1,0],[1,0,0,0,1]] #userInput(testMode)
    
    uInput = userInput(testMode)
    
    for i in range(4,-1,-1):
        hasAtleastOne = False
        for j in range(4,-1,-1):
            binaryInput = uInput[i][j]
            if binaryInput == 1:
                moveArmY(j+1)
                hasAtleastOne = True
        
        if hasAtleastOne:
            moveArmX(i+1)
        
    
if __name__ == "__main__":
    main()