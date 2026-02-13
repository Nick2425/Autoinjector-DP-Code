import time
import matplotlib as pl
import matplotlib.pyplot as plt 
import matplotlib.animation as anim
import numpy as np
import math

LOOP_DELAY = 0.1
FORCE_THRESHOLD = 0
HOLD_TIME = 3
time_passed = 0

def test_rolling_average():
    global time_passed
    data_list_1 = []
    time_list = []

    above_threshold = False
    time_pressed = 0

    ### PLOTLIB STUFF
    plt.ion()
    fig, ax = plt.subplots()
    ax.set_xlabel("Relative Time (s)", fontweight="bold")
    ax.set_ylabel("Force (N)", fontweight="bold")

    ax.set_xlim(-5, 0)
    ax.set_ylim(-5,260)

    ax.set_xticks([-5, -4, -3, -2, -1, 0])
    ax.set_yticks([0, 50, 100, 150, 200, 250])

    line: plt.Line2D = ax.plot(time_list, data_list_1)[0]
    
    #### MAIN FUNCTION THIGNS

    while above_threshold != True:
        data_list_1 = update_list(data_list_1)
        time_list = generate_time_list(len(data_list_1))
        rolling_average_1 = FSR_rolling_average(data_list_1) 
       
        #### Compares rolling averages
        if rolling_average_1 != None:
            if rolling_average_1 > FORCE_THRESHOLD:
                ### imcrements time the sensor is pushed for
                time_pressed += LOOP_DELAY
                # checks if sensor is held for hold time
                if time_pressed > HOLD_TIME:
                    above_threshold = True
        ### checks if person lets go and resets if necessary.
        else:
            if time_pressed > 0:
                time_pressed = 0
        print("------ROLLING AVERAGE--------------")
        print(rolling_average_1)

        time.sleep(LOOP_DELAY)
        time_passed+=LOOP_DELAY

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

###### CREATES SIMULATED FORCE VALUES BASED ON A TRAPEZOIDIAL SINE WAVE
def sim_force(): ## simulates force
    global time_passed
    value = max(0,min(1,2*(math.sin((time_passed - 2)))))
    return 210*value


##### APPENDS FORCE VALUES TO THE LIST
def update_list(inputed_list):
    updated_list = inputed_list.copy()
    if len(updated_list) < 30:
        updated_list.append(sim_force())
    else:
        updated_list.pop(0)
        updated_list.append(sim_force())
    return updated_list


### GENERATES A LIST OF TIMES DISPLAYED ON THE PLOT
def generate_time_list(n: int):
    time = []
    element = LOOP_DELAY * -1*n
    for i in range(n):
        time.append(element)
        element += LOOP_DELAY
    return time


####### ROLLING AVERAGE CODE COPIED
def FSR_rolling_average(datalist):
  if len(datalist) < 30:
    return None
  else:
    rolling_av = sum(datalist)/30
    return rolling_av




test_rolling_average()