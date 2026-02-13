import create_objects
import time
import gate
import rolling_average as rv
import matplotlib.pyplot as plt
from sensor_library import *

LOOP_DELAY = 0.05
FORCE_THRESHOLD = 200
HOLD_TIME = 3


def main(dosage_period = 0):
    
    ### Each return statement after main ensures that main() won't be called continuously.
    ###### INPUT INFORMATION BY DOCTOR ########
    if dosage_period == 0:
        try: ### CHECK TYPE OF INPUT
            dosage_period = float(input("Enter dosage period: "))    
        except:
            print("Error: Enter a number for the dosage period!")
            main()
            return 0
    try: #### CHECK TYPE OF INPUT
        dosage_count = input("Enter the dosage count: ")
        if str(int(dosage_count)) != dosage_count:
            print("Error: Enter an integer value for the dosage count!")
            main(dosage_period)
            return 0
    except:
        print("Error: Enter an integer value for the dosage count!")
        main(dosage_period)
        return 0
    print("Success!")

    ##### Establish objects
    devices = create_objects()
    #### Assign objects
    green_led = devices[0]
    red_led = devices[1]
    buzzer = devices[2]
    dc_motor = devices[3]
    actuator = devices[4]
    button_sensor = devices[5]
    #### Establish initial doses
    doses_administered = 0
    while doses_administered < dosage_count:
        gate_open = False
        green_led.on()


        ########### While the gate isn't --- program halts until the button is pressed and gate opens
        while gate_open == False:
            time.sleep(LOOP_DELAY) ### reduces cpu load on pi
            # Check the force sensor
            try:
                if button_sensor.force > FORCE_THRESHOLD:
                    gate_open = True
                    green_led.off()
                    gate.open(dc_motor, open=True)
            except:
                print("Error opening the gate")


        ###### Begin calculating the rolling average of FSRS
        ## Incorporate rolling average code here.

        ### Here the force data lists are predefined
        data_list = [[],[],[]] #### EMPTY DATA SETS
        FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3]
        RA_list = [] ### PREDEFINED ROLLING AVERAGE LIST
        time_list = []

        #### initial variables
        above_threshold = False
        time_pressed = 0

        ### MATPLOB LIB CONFIG
        plt.ion()
        fig, ax = generate_plot()
        fig.suptitle("Force Sensor Graphs")
        lines = [] ### DATA FROM THE SENSORS WILL BE DISPLAYED IN THESE LINES
        ###### CREATES LINES
        for i in range(3):
            line = ax[i].plot([], [])[0]
            lines.append(line)

        while above_threshold != True:

            ##### RA IS THE SAME AS ROLLING AVERAGE
            RA_list.clear() ### RESETS ROLLING AVERAGE LIST
            for i in range(3):
                data_list[i] = update_list(data_list[i], FSR_list[i])
                average = FSR_rolling_average(data_list[i])
                RA_list.append(average) ##REAPPENDS ROLLING AVERAGE LIST
            time_list = generate_time_list(len(data_list[0]))


            #### Compares rolling averages and checks if they are defined or are null
            if RA_list[0] != None and RA_list[1] != None and RA_list[2] != None:
                if RA_list[0] > FORCE_THRESHOLD and RA_list[1] > FORCE_THRESHOLD and RA_list[2] > FORCE_THRESHOLD:  ### imcrements time the sensor is pushed for
                    time_pressed += LOOP_DELAY                                                                      ### adjusts for unknown time delay
                    if time_pressed > HOLD_TIME:                                                                    ### checks if sensor is held for the total hold time
                        above_threshold = True 
                        break                                                                                       ### This exists the loop
                else:                           #### checks if person lets go and resets if necessary.
                    if time_pressed > 0:        #### Resets the hold time if the averages aren't all above 0
                        time_pressed = 0        #### which can imply that the device is in contact at the wrong angle and therefore can malfunction


            time.sleep(LOOP_DELAY)
            ##############################
            #### Matplotlib functions ####
            ##############################

            for i in range(3):
                lines[i].set_xdata(time_list)
                lines[i].set_ydata(data_list[i])
                ax[i].set_xlabel(f"Relative Time (s) | Rolling Average {i} = {RA_list[i]}", fontweight="bold")
                ax[i].relim()        
        
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(LOOP_DELAY) 
            rv.time_passed += LOOP_DELAY

        plt.ioff()
        plt.show()

        ##### Begin injection
        ##### Incorporate rolling average code here


        ##### Grace period after injection
        time.sleep(5)
        ##### Close the gate
        try:
            gate.open(dc_motor, open=False)
        except:
            print("Error closing the gate")
        ### Finishing the dose administration
        doses_administered += 1
        red_led.on()
        time.sleep(dosage_period) ### Waits for dosage period.

    #### End of autoinjector use - needs refill now.
    return 0


def update_list(inputed_list, sensor: Force_Sensing_Resistor):
    updated_list = inputed_list.copy()
    if len(updated_list) < 150: ### stores elements up to 150
        updated_list.append(sensor.force_raw())
    else:
        updated_list.pop(0)
        updated_list.append(sensor.force_raw())
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
    rolling_av = sum(datalist, -30)/30 #### Returns the rolling average of the latest 30 elements.
    return round(rolling_av, 2)
