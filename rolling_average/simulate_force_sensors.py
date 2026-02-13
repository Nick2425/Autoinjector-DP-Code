import time
import math
import random

time_passed = 0
class ra_simulators():
    def __init__(self, variability = 0) -> None:
        pass
        self.reading = 0
        self.variability = variability

    def read_force(self):
        global time_passed
        value = max(0,min(1,2*(math.sin((time_passed - 2 - random.uniform(-1*self.variability, self.variability))))))
        return 140*value
        