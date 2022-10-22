from utils.brick import Motor, wait_ready_sensors, reset_brick, configure_ports, TouchSensor
from time import sleep, time
import os 
import simpleaudio
from brickpi3 import BrickPi3
import multiprocessing

SAMPLES_FOLDER = "/home/pi/ecse211/MiniProject/Samples/"
MOTOR_LEFT = configure_ports(PORT_C=Motor)
MOTOR_RIGHT = configure_ports(PORT_B=Motor)
BP = MOTOR_LEFT.brick
KEY_BUFFER = 0.25
portLeft = BP.PORT_C
portRight = BP.PORT_B
threads = {}
threads["drums"] = None
drumDurations = [6.0,4.79,4.0,3.42,3.0]
touchSensors = [BP.PORT_1,BP.PORT_2,BP.PORT_3,BP.PORT_4]
wait_ready_sensors()

def motorConfig(motor, port):
    motor.set_limits(power = 30)
    current_position = BP.get_motor_status(port)[2]
    target_position = (((BP.get_motor_status(port)[2] // 360)+1) * 360) + 5 ;
    while abs(current_position - target_position) > 1:
        print(current_position)
        motor.set_position(target_position)
        current_position = BP.get_motor_status(port)[2]
        sleep(0.02)

def fluteConfig():
    flute = []
    fluteDir = SAMPLES_FOLDER+"Flute/"
    fluteSamplesDir = os.fsencode(fluteDir)

    for folder in sorted(os.listdir(fluteSamplesDir)):
        folderDir = fluteDir+os.fsdecode(folder)+"/"
        scale = []
        for sample in os.listdir(os.fsencode(folderDir)):
            samplePath = folderDir+os.fsdecode(sample)
            scale.append(simpleaudio.WaveObject.from_wave_file(samplePath))
        flute.append(scale)
    print("Flute samples loaded.")
    return flute

def drumsConfig():
    drums = []
    drumsDir = SAMPLES_FOLDER+"Drums/"
    
    for sample in sorted(os.listdir(os.fsencode(drumsDir))):
        print (os.fsdecode(sample))
        samplePath = drumsDir+os.fsdecode(sample)
        drums.append(simpleaudio.WaveObject.from_wave_file(samplePath))
        
    print("Drum samples loaded.")
    return drums

def convertToRelativePosition(absolutePosition):
    return (abs(absolutePosition)//60)

def loopDrums(sample,duration):
    while True:
        playObj = sample.play()
        sleep(duration+0.01)
    
def drums(relativePosition):
    global stopCurrentDrumLoop
    motorPositions[1] = relativePosition
    if threads["drums"] != None:
        threads["drums"].kill()
        threads["drums"].join()
        
    if relativePosition == 0:
        return

    threads["drums"] = multiprocessing.Process(target=loopDrums,args=(drumsObj[relativePosition-1],drumDurations[relativePosition-1]))
    threads["drums"].start()
    return     

def flute(relativePosition):
    motorPositions[0] = relativePosition

def playFlute(note):
    if motorPositions[0] == 0:
        return
    fluteNote = fluteObj[motorPositions[0]][note]
    playFluteNoteObj = fluteNote.play()

def main ():
    # SETTING DEPENDENCIES AND GLOBAL VARS
    global motorPositions
    motorPositions  = [0,0]
    global fluteObj
    fluteObj = fluteConfig()
    global drumsObj
    drumsObj = drumsConfig()
    motorConfig(MOTOR_LEFT, portLeft)
    motorConfig(MOTOR_RIGHT, portRight)
    reset_brick()

    # MAIN LOOP
    try:
        while True:
            leftMotorRelPos = convertToRelativePosition(BP.get_motor_status(portLeft)[2] % 360)
            rightMotorRelPos = convertToRelativePosition(BP.get_motor_status(portRight)[2] % 360)
        # DRUMS KNOB STATE UPDATE
            if rightMotorRelPos != motorPositions[1]:
                drums(rightMotorRelPos)
        # FLUTE KNOB STATE UPDATE
            if leftMotorRelPos != motorPositions[0]:
                flute(leftMotorRelPos)
        # FLUTE KEYS PRESSED
            #print(BP.get_sensor(touchSensors[0]))
        

            sleep(0.01)
            print(motorPositions)
    except KeyboardInterrupt as e:
        print(e)
        print("exited program")
        reset_brick()
        exit()

main()
