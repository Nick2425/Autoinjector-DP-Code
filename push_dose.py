
import time
from gpiozero import Motor
import ctypes

## Calculations for push time require how fast the actuator pushes and for what distance.
TIME_FOR_DOSE = 0
SPEED = 0



def push_dose(actuator: Motor):
    actuator.forward(speed=SPEED)
    time.sleep(TIME_FOR_DOSE)
    actuator.stop()