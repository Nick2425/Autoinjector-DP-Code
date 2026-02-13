import time
import math
import random


###### CREATES SIMULATED FORCE VALUES BASED ON A TRAPEZOIDIAL SINE WAVE


time_passed = 0
class ra_simulators():
    def __init__(self, variability = 0.000) -> None:
        pass
        self.reading = 0
        self.variability = variability

    def read_force(self):
        global time_passed
        value = max(0,min(1,2*(math.sin((time_passed - 2 - random.uniform(-0.555*self.variability, 0.555*self.variability))))))
        return 140*value
