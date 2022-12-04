from utils.brick import Motor
from time import sleep

motors = [Motor("C"), Motor("B")]

for motor in motors:
    motor.reset_encoder()
    motor.set_limits(power=30)
    motor.set_position(-180)

    
exit()

    
