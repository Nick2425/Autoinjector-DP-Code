import time
from gpiozero import Motor

TIME = 0.4
SPEED = 0.5


### This function uses the DC Motor to open the cover
def open(motor_object: Motor, open = True):
    if open == True:
        motor_object.forward(speed=SPEED)
        time.sleep(TIME)
        motor_object.stop()
    else:
        motor_object.backward(speed=SPEED)
        time.sleep(TIME)
        motor_object.stop()


def test_gate():
    DC_MOTOR_PIN = (12, 16)  # forward, backward
    MOTOR_TEST = Motor(forward=DC_MOTOR_PIN[0], backward=DC_MOTOR_PIN[1])

    open(MOTOR_TEST)
    time.sleep(5)
    open(MOTOR_TEST, False)