import math
import sys
from gpiozero import Servo
#Radius = #enter radius
#Conver_Constant = math.pi * Radius * 2
my_servo = Servo(17,min_pulse_width=0.75/1000, max_pulse_width=2.25/1000)
def test():
  servo.value=-1
  time.sleep(2)
  servo.value=0
  time.sleep(2)
  servo.value=1
test()
