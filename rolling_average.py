from sensor_library import *

FSR1=Force_Sensing_Resistor(0)
FSR2=Force_Sensing_Resistor(1)
FSR3=Force_Sensing_Resistor(2)

### this calculates and returns the rolling average of a list of data.
def FSR_rolling_average(datalist):
  if len(datalist) < 30:
    return None
  else:
    rolling_av = sum(datalist)/30
    return round(rolling_av,2)

### This takes in a list of force values and adds the latest force value and removes the oldest if necessary -- returns the new force list.
def update_list(inputed_list, sensor: Force_Sensing_Resistor):
    updated_list = inputed_list.copy()
    if len(updated_list) < 30:
        updated_list.append(sensor.force_raw())
    else:
        updated_list.pop(0)
        updated_list.append(sensor.force_raw())
    return updated_list

