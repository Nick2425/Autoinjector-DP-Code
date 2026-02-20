import math
import sys
import time
from gpiozero import Servo
#Radius = #enter radius
#Conver_Constant = math.pi * Radius * 2
servo = Servo(26,min_pulse_width=0.00055, max_pulse_width=0.00235)
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / Conver_Constant)*(2/1.7))-1
  return distance
