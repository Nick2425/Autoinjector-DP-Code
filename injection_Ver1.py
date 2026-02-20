import math
import sys
import time
from gpiozero import Servo
#Radius = #enter radius
#CONVER_CONSTANT = math.pi * Radius * 2
servo = Servo(26,min_pulse_width=0.00055, max_pulse_width=0.00235)
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = round(((current_amount / CONVER_CONSTANT)*(2/1.7)),1)-1
  return distance
  
