from utils.brick import Motor, wait_ready_sensors, reset_brick, configure_ports, TouchSensor
from time import sleep, time
import os 
import simpleaudio
import threading


SAMPLES_FOLDER = "/home/pi/ecse211/MiniProject/Samples/"
KEY_BUFFER = 0.25
threads = {}
threads["drums"] = None
drumDurations = [6.0,6.0,4.79,4.0,3.42,3.0]
stopCurrentDrums = False
touchSensors = [TouchSensor(1),TouchSensor(2),TouchSensor(3),TouchSensor(4)]
wait_ready_sensors()

def motorConfig(motor):
    motor.set_limits(power = 30)
    current_position = motor.get_position()
    target_position = (((motor.get_position() // 360)+1) * 360) + 5 ;
    while abs(current_position - target_position) > 1:
        motor.set_position(target_position)
        current_position = motor.get_position()
        sleep(0.02)
    motor.float_motor()

            

def fluteConfig():
    flute = []
    fluteDir = SAMPLES_FOLDER+"Flute/"
    fluteSamplesDir = os.fsencode(fluteDir)

    for folder in sorted(os.listdir(fluteSamplesDir)):
        folderDir = fluteDir+os.fsdecode(folder)+"/"
        scale = []
        for sample in sorted(os.listdir(os.fsencode(folderDir))):
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

def loopDrums(sample,duration,stop):
    while True:
        playObj = sample.play()
        sleep(duration+0.01)
        if stop():
            break
    
def drums(relativePosition):
    motorPositions[1] = relativePosition
    global stopCurrentDrums
    if threads["drums"] != None:
        stopCurrentDrums = True
        threads["drums"].join()
        stopCurrentDrums = False
        
    
    threads["drums"] = threading.Thread(target=loopDrums,args=(drumsObj[relativePosition],drumDurations[relativePosition],lambda : stopCurrentDrums))
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
    global killSwitch
    killSwitch = Motor("A")
    killSwitch.reset_encoder()
    killSwitch.float_motor()
    
    
    drums(motorPositions[0])

    # MAIN LOOP
    while True:
        try:
            
        #GLOBAL KILL SWITCH
            if (killSwitch.get_position() % 360) > 20 and (killSwitch.get_position() % 360) < 340 :
                raise KeyboardInterrupt
            
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
