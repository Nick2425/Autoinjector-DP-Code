import create_objects
import time
import gate
import rolling_average as rv
import matplotlib.pyplot as plt
from sensor_library import *
from gpiozero import Buzzer
from gpiozero import Motor
from gpiozero import Servo
from gpiozero import LED
import push_dose


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

    ### type check
    dosage_count = int(dosage_count)
    dosage_period=int(dosage_period)

    ##### Establish objects
    devices = create_objects.create_objects()

    #### Assign objects and enforce types
    green_led: LED = devices[0]
    red_led: LED = devices[1]
    buzzer: Buzzer = devices[2]
    dc_motor: Motor = devices[3]
    servo: Servo = devices[4]
    button_sensor: Force_Sensing_Resistor = devices[5]

    ### MATPLOB LIB CONFIG
    plt.ion()

    try:
        fig, ax = generate_plot()
        fig.suptitle("Sensor and Output Device Data")
        lines = [] ### DATA FROM THE SENSORS WILL BE DISPLAYED IN THESE LINES
        ###### CREATES LINES
        for i in range(3):
            line = ax[i, 0].plot([], [])[0]
            lines.append(line)
        lines.append(ax[2, 1].plot([], [])[0])
        ### Here the force data lists are predefined

    except:
        print("Error with initial plotting!")

    update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)
    time_list = []
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3, button_sensor]
    plt.tight_layout()

    #### Establish initial doses
    doses_administered = 0
    while doses_administered < dosage_count:
        gate_open = False
        green_led.on()
        update_led_bars([red_led.is_active,green_led.is_active], ax, fig)

        ### ACTIVATE BUZZER HERE
        #buzzer.on()
        ### Here the force data lists are predefined
        data_list = [[],[],[],[]] #### EMPTY DATA SETS
        RA_list = [] ### PREDEFINED ROLLING AVERAGE LIST
        time_list = []

        #### initial variables
        above_threshold = False
        time_pressed = 0

        plt.tight_layout()
        ########### While the gate isn't --- program halts until the button is pressed and gate opens
        while gate_open == False:
            plt.pause(LOOP_DELAY) ### reduces cpu load on pi
            data_list[3] = update_list(data_list[3], FSR_list[3])
            time_list = generate_time_list(len(data_list[3]))

            # Check the force sensor
            try:
                if button_sensor.force_raw() > FORCE_THRESHOLD:
                    gate_open = True
                    green_led.off()
                    #buzzer.off()
                    gate.open(dc_motor, open=True)
            except:
                print("Error opening the gate")

        update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
        update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)

        ###### Begin calculating the rolling average of FSRS
        ## Incorporate rolling average code here.

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


            plt.pause(LOOP_DELAY)
            ##############################
            #### Matplotlib functions ####
            ##############################

            for i in range(3):
                lines[i].set_xdata(time_list)
                lines[i].set_ydata(data_list[i])
                ax[i,0].set_xlabel(f"Relative Time (s) | Rolling Average {i} = {RA_list[i]}", fontweight="bold")
                ax[i,0].relim()  

            ax[2, 1].set_xlabel(f"Relative Time (s) | Press Time = {round(time_pressed,2)}", fontweight="bold")
            lines[3].set_xdata(time_list)
            lines[3].set_ydata(data_list[3])
        
            fig.canvas.draw()
            fig.canvas.flush_events()
            plt.pause(LOOP_DELAY) 
            rv.time_passed += LOOP_DELAY
            update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
            update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)


        ##### Begin injection
        ##### Incorporate rolling average code here

        push_dose.push_dose(servo)
        update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
        update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)

        ##### Grace period after injection
        plt.pause(5)
        ##### Close the gate
        try:
            gate.open(dc_motor, open=False)
        except:
            print("Error closing the gate")
        ### Finishing the dose administration
        doses_administered += 1
        red_led.on()
        update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
        update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)

        plt.pause(dosage_period) ### Waits for dosage period.

    #### End of autoinjector use - needs refill now.
    plt.ioff()
    plt.show()

    return 0




### GENERATES PLOTS
def generate_plot():
    fig, ax = plt.subplots(3, 2)
    for i in range(3):
        ax[i,0].set_xlim(-3, 0)
        ax[i,0].set_ylim(-3,160)
        ax[i,0].set_xlabel("Relative Time (s)", fontweight="bold")
        ax[i,0].set_ylabel("Force (N)", fontweight="bold")

        ax[i,0].set_xticks([-3, -2, -1, 0])
        ax[i,0].set_yticks([0, 50, 100, 150])
    ### LEDS
    ax[0,1].set_xlabel("LED Color")
    ax[0,1].set_ylabel("LED Status")
    ### OTHER OUTPUT DEVICE STATUS
    ax[1,1].set_xlabel("Output Type")
    ax[1,1].set_ylabel("Output Status")

    ### BUTTON FORCE SENSOR STATUS
    ax[2,1].set_xlim(-3, 0)
    ax[2,1].set_ylim(-3,160)
    ax[2,1].set_xlabel("Relative Time (s)", fontweight="bold")
    ax[2,1].set_ylabel("Force (N) Button", fontweight="bold")

    ax[2,1].set_xticks([-3, -2, -1, 0])
    ax[2,1].set_yticks([0, 50, 100, 150])

    return fig, ax
####### THIS UPDATES THE STORED FORCE VALUES IN THE LIST AFTER REACHING MAXIMUM CAPACITY
def update_list(inputed_list, sensor: Force_Sensing_Resistor):
    updated_list = inputed_list.copy()
    if len(updated_list) < 150: ### stores elements up to 150
        updated_list.append(sensor.force_raw())
    else:
        updated_list.pop(0)
        updated_list.append(sensor.force_raw())
    return updated_list

### GENERATES A LIST OF RELATIVE TIMES DISPLAYED ON THE PLOT
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
  
### UPDATES LED BAR GRAPH
def update_led_bars(data, ax, fig):
    colors = ['Red LED', 'Green LED']
    bar_colors = ['tab:red', 'tab:green']
    ax[0,1].clear()
    ax[0,1].bar(colors, data, color = bar_colors)[0] 
    fig.canvas.draw()
    fig.canvas.flush_events()


### updates the graph of the other outputs
def update_other_outputs(data, ax, fig):
    labels_graph_1 = ['Servo Motor', 'DC Motor', 'Buzzer']
    bar_colors = ['tab:blue', 'tab:purple', 'tab:red']
    ax[1,1].clear()
    ax[1,1].bar(labels_graph_1, data, color = bar_colors)[0] 
    fig.canvas.draw()
    fig.canvas.flush_events()
