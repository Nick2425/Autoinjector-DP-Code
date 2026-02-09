# Jan 29th 2026
# Nick Kuijpers
# SN: 400619254
# This script instantiates the raspberry pi objects.

# Import Output Devices
from gpiozero import Buzzer
from gpiozero import Motor
from gpiozero import LED
from sensor_library import *
# Import sensor devics
from sensor_library import *

import time
import sys

# NUMBERS BELOW ARE PLACEHOLDERS
GREEN_LED_PIN = 0
RED_LED_PIN = 1
BUZZER_PIN = 2
DC_MOTOR_PIN = (3, 4)  # forward, backward
ACTUATOR_PIN = (5, 6) # forward, backward
BUTTON_PIN = 7

def create_objects():
    green_led = LED(GREEN_LED_PIN)
    red_led = LED(RED_LED_PIN)

    buzzer = Buzzer(BUZZER_PIN)
    dc_motor = Motor(forward=DC_MOTOR_PIN[0], backward=DC_MOTOR_PIN[1])
    actuator = Motor(ACTUATOR_PIN[0], ACTUATOR_PIN[1])

    fsr = Force_Sensing_Resistor(BUTTON_PIN)
    return green_led, red_led, buzzer, dc_motor, actuator, fsr