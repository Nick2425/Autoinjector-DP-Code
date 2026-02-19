import time
from gpiozero import Servo


def push_dose(motor: Servo, open = True):
    if open == True:
        motor.value = -1
    else:
        motor.value = 1

SERVO_PIN = 26
SERVO_TEST = Servo(SERVO_PIN)

def test_servo():
    SERVO_TEST.max()
    time.sleep(5)
    SERVO_TEST.min()



