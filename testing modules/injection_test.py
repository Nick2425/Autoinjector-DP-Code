import math
import sys
import time
from gpiozero import Servo
Radius = 5
Conver_Constant = math.pi * Radius * 2
servo = Servo(26,min_pulse_width=0.00055, max_pulse_width=0.00235)
def inject_amount(count, dosage):
    current_amount = (count+1) * dosage
    distance = round(((current_amount / Conver_Constant)*(2/1.7)),1)-1
    return distance
dosage = 2
servo.min()
for i in range(5):
  servo.value(inject_amount(i,dosage))

