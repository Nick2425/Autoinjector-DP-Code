import time
import matplotlib as pl
import matplotlib.pyplot as plt 
import matplotlib.animation as anim
import rolling_average as rv
import numpy as np
import math

LOOP_DELAY = 0.05
FORCE_THRESHOLD = 0
HOLD_TIME = 3

def test_rolling_average():

    data_list_1 = []
    data_list_2 = []
    data_list_3 = []
    time_list = []
    above_threshold = False
    time_pressed = 0
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("Relative Time (s)", fontweight="bold")
    ax.set_ylabel("Force (N)", fontweight="bold")

    ax.set_xlim(-5, 0)
    ax.set_ylim(-5,260)

    ax.set_xticks([-5, -4, -3, -2, -1, 0])
    ax.set_yticks([0, 50, 100, 150, 200, 250])

    line = ax.plot(time_list, data_list_1)[0]
    
    while above_threshold != True:
        data_list_1 = rv.update_list(data_list_1, rv.FSR1)
        data_list_2 = rv.update_list(data_list_2, rv.FSR2)
        data_list_3 = rv.update_list(data_list_3, rv.FSR3)

        rv1 = rv.FSR_rolling_average(data_list_1) ##rolling average 1
        rv2 = rv.FSR_rolling_average(data_list_2) ##rolling average 2
        rv3 = rv.FSR_rolling_average(data_list_3) ##rolling average 3

        #### Compares rolling averages
        if rv1 != None and rv2 != None and rv3 != None:
            if rv1 > FORCE_THRESHOLD and rv2 > FORCE_THRESHOLD and rv3 > FORCE_THRESHOLD: 
                ### imcrements time the sensor is pushed for
                time_pressed += 3*LOOP_DELAY #### adjusts for unknown time delay
                # checks if sensor is held for hold time
                if time_pressed > HOLD_TIME:
                    above_threshold = True
            ### checks if person lets go and resets if necessary.
            else:
                if time_pressed > 0:
                    time_pressed = 0



        time.sleep(LOOP_DELAY)
        ##############################
        #### Matplotlib functions ####
        ##############################

        line.set_xdata(time_list)
        line.set_ydata(data_list_1)
        
        # Rescale axes automatically if needed
        ax.relim()
        ax.autoscale_view()
    
        fig.canvas.draw()
        fig.canvas.flush_events()
        plt.pause(LOOP_DELAY) # Pause to allow the GUI event loop to run

    plt.ioff()
    plt.show()

print("Done")

def generate_time_list(n: int):
    time = []
    element = LOOP_DELAY * -1*n
    for i in range(n):
        time.append(element)
        element += LOOP_DELAY
    return time
