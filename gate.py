import time
from gpiozero import Motor # type: ignore

# TIME CALCULATIONS NECESSARY FROM GEAR TRAIN
TORQUE = 2.75/100 # 0.00275 Kg*M
RPM = 80 # revolutions per minute
TIME = 5
SPEED: int = 1

def open(motor: Motor, open: bool = True):
    if open == True:
        motor.forward(speed=SPEED)
        time.sleep(TIME)
        motor.stop()
    else:
        motor.backward(speed=SPEED)
        time.sleep(TIME)
        motor.stop()

