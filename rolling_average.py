from sensor_library import *

FSR1=Force_Sensing_Resistor(0)
FSR2=Force_Sensing_Resistor(1)
FSR3=Force_Sensing_Resistor(2)
time_passed = 0

def FSR_rolling_average(datalist):
  if len(datalist) < 50:
    return None
  else:
    rolling_av = sum(datalist)/50
    return rolling_av

def update_list(inputed_list, sensor: Force_Sensing_Resistor):
    updated_list = inputed_list.copy()
    if len(updated_list) < 50:
        updated_list.append(sensor.force_raw())
    else:
        updated_list.pop(0)
        updated_list.append(sensor.force_raw())
    return updated_list

