from sensor_library import *


FSR1=Force_Sensing_Resistor(0)
FSR2=Force_Sensing_Resistor(1)
FSR3=Force_Sensing_Resistor(2)

def FRS1_rolling(datalist, sensor):
  if len(datalist) < 50:
    return None
  else:
    datalist.pop(0)
    daatalist.append(sensor.force_raw())
    rolling_av = sum(datalist)/50
    return rolling_av


  

