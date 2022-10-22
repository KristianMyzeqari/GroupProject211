from utils.brick import Motor, wait_ready_sensors, reset_brick, configure_ports, TouchSensor
from time import sleep, time
import os 
import simpleaudio
import multiprocessing


SAMPLES_FOLDER = "/home/pi/ecse211/MiniProject/Samples/"
KEY_BUFFER = 0.25
threads = {}
threads["drums"] = None
drumDurations = [6.0,4.79,4.0,3.42,3.0]
touchSensors = [TouchSensor(1),TouchSensor(2),TouchSensor(3),TouchSensor(4)]
wait_ready_sensors()

def motorConfig(motor):
    motor.set_limits(power = 30)
    current_position = motor.get_position()
    target_position = (((motor.get_position() // 360)+1) * 360) + 5 ;
    while abs(current_position - target_position) > 1:
        print(current_position)
        motor.set_position(target_position)
        current_position = motor.get_position()
        sleep(0.02)
    motor.float_motor()

def killAllThreads(*args):
    for t in threads.keys():
        if threads[t] != None:
            threads[t].kill()
            threads[t].join()
            print("threads killed")
            

def fluteConfig():
    flute = []
    fluteDir = SAMPLES_FOLDER+"Flute/"
    fluteSamplesDir = os.fsencode(fluteDir)

    for folder in sorted(os.listdir(fluteSamplesDir)):
        folderDir = fluteDir+os.fsdecode(folder)+"/"
        scale = []
        for sample in sorted(os.listdir(os.fsencode(folderDir))):
            samplePath = folderDir+os.fsdecode(sample)
            print(os.fsdecode(sample))
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
    fluteNote = fluteObj[motorPositions[0]-1][note]
    playFluteNoteObj = fluteNote.play()
    

def main ():
    # SETTING DEPENDENCIES AND GLOBAL VARS

    global motorPositions
    motorPositions  = [0,0]
    global fluteObj
    fluteObj = fluteConfig()
    global drumsObj
    drumsObj = drumsConfig()
    global motors
    motors = [Motor("C"),Motor("B")]
    motorConfig(motors[0])
    motorConfig(motors[1])
    print(fluteObj)

    # MAIN LOOP
    while True:
        try:
            leftMotorRelPos = convertToRelativePosition(motors[0].get_position() % 360)
            rightMotorRelPos = convertToRelativePosition(motors[1].get_position() % 360)
        # DRUMS KNOB STATE UPDATE
            if rightMotorRelPos != motorPositions[1]:
                drums(rightMotorRelPos)
            # FLUTE KNOB STATE UPDATE
            if leftMotorRelPos != motorPositions[0]:
                flute(leftMotorRelPos)
            # FLUTE KEYS PRESSED
            if touchSensors[0].is_pressed():
                playFlute(0)
            elif touchSensors[1].is_pressed():
                playFlute(1)
            elif touchSensors[2].is_pressed():
                playFlute(2)
            elif touchSensors[3].is_pressed():
                playFlute(3)

            sleep(0.075)
            #print(motorPositions)
        except KeyboardInterrupt as e:

            #print(e)
            print("exited program")
            reset_brick()
            exit()

main()