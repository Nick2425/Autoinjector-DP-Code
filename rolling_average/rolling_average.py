from sensor_library import *
var0=Force_Sensing_Resistor(0)
var1=Force_Sensing_Resistor(1)
var2=Force_Sensing_Resistor(2)
zlist=[]
olist=[]
tlist=[]

def rolling_average_0():
    global zlist
    while len(zlist) <= 50:
        zlist.append(var0.force_raw())
    zlist.pop(0)
    zlist.append(var0.force_raw())
    av = sum(zlist)/50
    if av > 230:
        return True
    else:
        return False

def rolling_average_1():
    global olist
    while len(olist) <= 50:
        olist.append(var1.force_raw())
    olist.pop(0)
    olist.append(var1.force_raw())
    av = sum(olist)/50
    if av > 230:
        return True
    else:
        return False

def rolling_average_2():
    global tlist
    while len(tlist) <= 50:
        tlist.append(var2.force_raw())
    tlist.pop(0)
    tlist.append(var2.force_raw())
    av = sum(tlist)/50
    if av > 230:
        return True
    else:
        return False
        

def decision():
    if var0.force_raw() > 20 and var1.force_raw() > 20 and var2.force_raw() > 20:
        if rolling_average_0() and rolling_average_1() and rolling_average_2() is True:
            return True
        else:
            return False