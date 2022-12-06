# // MODULE IMPORTS

from utils.brick import Motor, reset_brick, TouchSensor, wait_ready_sensors, EV3ColorSensor
from time import sleep
import simpleaudio as s



# // CONSTANTS DECLARATION

testMode = False
SAMPLES_FOLDER = "/home/pi/ecse211/FinalProject/Samples/"
beeps = [s.WaveObject.from_wave_file(SAMPLES_FOLDER+"SimpleBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"LongBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"DoubleBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"TripleBeep.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"Error.wav"),s.WaveObject.from_wave_file(SAMPLES_FOLDER+"ErrorSpeech.wav")]
motors = ((Motor("C"),Motor("B")),(Motor("A"),Motor("D")))
centerCubeOffset = 1.25
armOffset = 7.35
topArmOffset = 1
angleRatioCoefficient = 360/13.15
extraRewind = 20
powerVal = 100
sleepTime = -0.016*powerVal + 2.5

# // FUNCTIONS

# This function plays a given sound from the beeps sound bank
# Arguments:
# beepIndex: index of the beeps list representing the sound to be played
def playBeep(beepIndex):
    beep = beeps[beepIndex]
    beepObj = beep.play()

#This function generates and returns the 2D array containing the mosaic layout based on the user's input
# Arguments: 
# testMode: boolean value representing the input type (True for keyboard input, False for touch sensors input)
# Returns: 2D array containing the mosaic layout based on the user's input
def userInput(testMode:bool) -> list[list[int],list[int],list[int],list[int],list[int]]:
    
    userInput = [[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0],[0,0,0,0,0]]
    
    if testMode:
        nOnes = 0
        nInputs = 0
        print("Please enter binary input:")
        for i in range(0,5):
            for j in range(0,5):
                uInput = input(f"[{i},{j}] > ")
                if (uInput == "exit"):
                    exit()
                while uInput not in ["0","1"]:
                    print("input was not binary, try again:")
                    uInput = input(f"[{i},{j}] > ")
                userInput[i][j] = int(uInput)
                nInputs += 1
                if int(uInput) == 1:
                    nOnes+=1
                if nOnes == 16:
                    print("ERROR: Mosaic contains too many cubes (max: 15)")
                    sleep(0.5)
                    playBeep(4)
                    sleep(1.5)
                    playBeep(5)
                    return 0
                    
    else:
            
        touchSensors = [TouchSensor(3),TouchSensor(4),TouchSensor(2)]
        wait_ready_sensors()
        nOnes = 0
        tooMany = False
            
        for i in range(0,5):
            for j in range(0,5):
                binInput = None #0 by default
                takingInput = True
                
            
                
                print("Please give input for " + getName(i, j))
                
                while takingInput:
                    
                    if touchSensors[0].is_pressed():
                        print("Choose 0 for " + getName(i, j) + "?")
                        binInput = 0
                        playBeep(0)

                                
                    elif touchSensors[1].is_pressed():
                        print("Choose 1 for " + getName(i, j) + "?")
                        binInput = 1
                        playBeep(0)

                    elif touchSensors[2].is_pressed():
                        
                        if binInput == 1:
                            nOnes+=1
                        if binInput == None:
                            continue
                        else:
                            print("")
                            print(str(binInput) + " chosen for " + getName(i, j))
                            print("")
                            userInput[i][j]=(binInput)
                        if nOnes >= 16:
                            print("ERROR: Mosaic contains too many cubes (max: 15)")
                            sleep(0.5)
                            playBeep(4)
                            sleep(1.5)
                            playBeep(5)
                            return 0
                        else:
                            playBeep(1)
                        takingInput = False

                    sleep(.25)      
            #done with 1 row
            sleep(1.1)
            
                
        #done with input
        playBeep(2)
        sleep(1.1)
        

    return userInput

# this function transforms grid integer coordinates into the alphanumerical grid coordinates
# Arguments:
# row: integer representing row number, column: integer representing column number
# Returns: String containing alphanumerical grid coordinates
def getName(row, column):
    ret = ""
    if (row == 0):
        ret = ret + "A"
    if (row == 1):
        ret = ret + "B"
    if (row == 2):
        ret = ret + "C"
    if (row == 3):
        ret = ret + "D"
    if (row == 4):
        ret = ret + "E"
        
    if (column == 0):
        ret = ret + "1"
    if (column == 1):
        ret = ret + "2"
    if (column == 2):
        ret = ret + "3"
    if (column == 3):
        ret = ret + "4"
    if (column == 4):
        ret = ret + "5"
        
    return ret
    
# This function detects if the number of cubes specified in the argument have been loaded into the system. 
# Arguments:
# amount: integer representing the amount of cubes that need to be loaded before the system exits the Cube Loading State   
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
    print("")
    playBeep(3)
    
# This function sets the power of all of the system's motors to the global constant powerVal = 100%
def motorConfig():
    for t in motors:
        for m in t:
            m.set_limits(power = powerVal)

#This function moves the (wall pusher) by x (grid coordinates) and then goes back to initial position
# Argument
# x: integer representing the row the wall pusher has to travel to (grid coordinate)
def moveArmX(x:int):
    xbar = (4*x - 2) -centerCubeOffset + topArmOffset
    rotationX = angleRatioCoefficient * xbar
    motors[1][0].set_position_relative(-rotationX)
    motors[1][1].set_position_relative(-rotationX)
    sleep(sleepTime)
    motors[1][0].set_position_relative(rotationX + extraRewind)
    motors[1][1].set_position_relative(rotationX + extraRewind)
    sleep(sleepTime)
    
#This function moves the (claw arm pusher) by y (grid coordinates) and then goes back to initial position
# Argument
# y: integer representing the row the claw arm pusher has to travel to (grid coordinate)
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
    playBeep(2)
    detectCubes(15)
    
    uInput = userInput(testMode)
    
    while uInput == 0:
        uInput = userInput(testMode)
    

    # building algorithm
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
