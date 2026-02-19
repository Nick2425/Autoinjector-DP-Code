import math
import sys
from gpiozero import Servo
#Radius = #enter radius
#Conver_Constant = math.pi * Radius * 2
servo = Servo (26)
def test():
  servo.value=-1
  time.sleep(2)
  servo.value=0
  time.sleep(2)
  servo.value=1
test()
