import time
import matplotlib as pl # type: ignore
import matplotlib.pyplot as plt 
import rolling_average as rv
import numpy as np # type: ignore
import math # type: ignore

LOOP_DELAY = 0.05
FORCE_THRESHOLD = 0
HOLD_TIME = 3

def test_rolling_average():

    data_list: list[list[float]] = [[],[],[]] #### EMPTY DATA SETS
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3] #### FORCE SENSOR LIST
    RA_list: object = [] ### PREDEFINED ROLLING AVERAGE LIST
    time_list = []

    above_threshold = False
    time_pressed = 0

    ### MATPLOB LIB
    plt.ion() # type: ignore
    fig, ax = generate_plot()
    fig.suptitle("Force Sensor Graphs") # type: ignore
    lines = [] ### DATA FROM THE SENSORS WILL BE DISPLAYED IN THESE LINES

    ###### CREATES LINES
    for i in range(3):
        line = ax[i].plot([], [])[0]
        lines.append(line) # type: ignore
    ###### THIS IS THE REGULAR SENSING STUFF NOW
    
    while above_threshold != True:
        for i in range(3):
            data_list[i] = rv.update_list(data_list[i], FSR_list[i]) # type: ignore
        RA_list.clear() ### RESETS ROLLING AVERAGE LIST
        for i in range(3):
            RA_list.append(rv.FSR_rolling_average(data_list[i])) ##RE APPENDS ROLLING AVERAGE LIST # type: ignore

        #### Compares rolling averages
        if RA_list[0] != None and RA_list[1] != None and RA_list[2] != None:
            if RA_list[0] > FORCE_THRESHOLD and RA_list[1] > FORCE_THRESHOLD and RA_list[2] > FORCE_THRESHOLD: 
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

        for i in range(3):
            lines[i].set_xdata(time_list) # type: ignore
            lines[i].set_ydata(data_list[i]) # type: ignore
        
        # Rescale axes automatically if needed
        for i in range(3):
            ax[i].relim()
            ax[i].autoscale_view()
        
        fig.canvas.draw() # type: ignore
        fig.canvas.flush_events()
        plt.pause(LOOP_DELAY) # Pause to allow the GUI event loop to run

    plt.ioff() # type: ignore
    plt.show() # type: ignore

print("Done")

def generate_time_list(n: int) -> list[float]:
    time: list[float] = []
    element = LOOP_DELAY * -1*n
    for i in range(n): # type: ignore
        time.append(element)
        element += LOOP_DELAY
    return time

def generate_plot():
    fig, ax = plt.subplots(3) # type: ignore
    for i in range(3):
        ax[i].set_xlabel("Relative Time (s)", fontweight="bold")
        ax[i].set_ylabel("Force (N)", fontweight="bold")

        ax[i].set_xlim(-5, 0)
        ax[i].set_ylim(-5,260)

        ax[i].set_xticks([-5, -4, -3, -2, -1, 0])
        ax[i].set_yticks([0, 50, 100, 150, 200, 250])

    return fig, ax

