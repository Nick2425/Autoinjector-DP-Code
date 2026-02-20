import math
import sys
import time
from gpiozero import Servo
#Radius = #enter radius
#CONVER_CONSTANT = math.pi * Radius * 2
CONVER_CONSTANT = 6*math.pi
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / CONVER_CONSTANT)*(2/1.7))-1
  return distance
