import time
from gpiozero import Servo


def push_dose(motor: Servo, open = True):
    if open == True:
        motor.value = -1
    else:
        motor.value = 1

def test_servo():
    SERVO_TEST = Servo(26)
    SERVO_TEST.max()
    time.sleep(5)
    SERVO_TEST.min()



