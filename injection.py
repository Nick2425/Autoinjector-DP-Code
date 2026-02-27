import math
import sys
import time
from gpiozero import Servo
CONVER_CONSTANT = 0.4*2*math.pi ### The cross sectional area of our syringe.

### This function calculates total volume of medication delivered to date relative to the next dose
### and divides it by the cross sectional area of the syringe to get the height distance that the servo actuator must 
### move to in centimeters -- this is converted into a position value between 1 and -1 and is returned.

def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / CONVER_CONSTANT)*(2/1.7))-1
  return distance
