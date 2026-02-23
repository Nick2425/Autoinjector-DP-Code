# Jan 29th 2026
# Nick Kuijpers
# SN: 400619254
# This script instantiates the raspberry pi devices' objects.

# Import Output Devices
from gpiozero import Buzzer
from gpiozero import Motor
from gpiozero import Servo
from gpiozero import LED
from sensor_library import *
# Import sensor devics
from sensor_library import *

import time
import sys

# NUMBERS BELOW ARE PLACEHOLDERS
GREEN_LED_PIN = 21
RED_LED_PIN = 20
BUZZER_PIN = 5
DC_MOTOR_PIN = (12, 16)  # forward, backward
SERVO_PIN = 26
BUTTON_PIN = 3

GREEN_LED = LED(GREEN_LED_PIN)
RED_LED = LED(RED_LED_PIN)
BUZZER = Buzzer(BUZZER_PIN)
DC_MOTOR = Motor(forward=DC_MOTOR_PIN[0], backward=DC_MOTOR_PIN[1])
SERVO: Servo = Servo(SERVO_PIN, initial_value=-1 min_pulse_width=0.00055, max_pulse_width=0.00235)

FSR = Force_Sensing_Resistor(BUTTON_PIN)
