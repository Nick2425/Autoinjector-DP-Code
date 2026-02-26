import create_objects
import gate
import rolling_average as rv
import matplotlib.pyplot as plt
from sensor_library import *
from gpiozero import Buzzer
from gpiozero import Motor
from gpiozero import Servo
from gpiozero import LED
import injection

LOOP_DELAY = 0.01
FORCE_THRESHOLD = 100
HOLD_TIME = 3
SYRINGE_VOLUME = 10 ## PLACEHOLDER


def main(dosage_period = 0):
    #### THIS ASSIGNS OBJECTS TO VARIABLES
    green_led = create_objects.GREEN_LED
    red_led = create_objects.RED_LED
    buzzer = create_objects.BUZZER
    dc_motor = create_objects.DC_MOTOR
    servo = create_objects.SERVO
    button_sensor = create_objects.FSR
    dosage_amount = 0

    servo.detach()


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
        dosage_amount = input("Enter the dosage amount in mL: ")
        if str(int(dosage_amount)) != dosage_amount:
            print("Error: Enter an integer value for the dosage amount!")
            main(dosage_period)
            return 0
    except:
        print("Error: Enter an integer value for the dosage amount!")
        main(dosage_period)
        return 0
    print("Success!")



    ### ESTABLISHES AMOUNT OF DOSES AND PERIOD
    dosage_amount = int(dosage_amount)
    dosage_period = int(dosage_period)

    ### MATPLOB LIB CONFIGURATION
    plt.ion()

    try:
        fig, ax = generate_plot()
        fig.suptitle("Sensor and Output Device Data")
        lines = [] ### DATA FROM THE FORCE SENSORS WILL BE DISPLAYED IN THESE LINES
        ###### CREATES LINES
        for i in range(3):
            line = ax[i, 0].plot([], [])[0]
            lines.append(line)
        lines.append(ax[2, 1].plot([], [])[0])
        ax[2, 1].set_xlabel(f"Relative Time (s)", fontweight="bold")

    except:
        print("Error with initial plotting!")
    finally:
        pass ### CODE CONTINUES TO RUN DESPITE ENCOUNTERING GRAPH ISSUES

    ############### TIME LIST DEFINITION AND FORCE SENSOR OBJECTS ################
    time_list = []
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3, button_sensor]

    #################################################### GRAPH DATA UPDATES ################################3
    update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
    update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)
    #################################################### GRAPH DATA UPDATES ################################3
    plt.tight_layout()

    #### ESTABLISH INITIAL DOSAGE COUNT AND DOSES ADMINISTERED
    doses_administered = 0
    dosage_count = SYRINGE_VOLUME / dosage_amount


    ###### MAIN LOOP BEGINS HERE #####################
    while doses_administered < dosage_count:

        ######### initialize gate, graphs and LEDs
        red_led.off()
        gate_open = False
        green_led.on()
        
        #################################################### GRAPH DATA UPDATES ################################3
        update_led_bars([red_led.is_active,green_led.is_active], ax, fig)
        update_other_outputs([servo.is_active, dc_motor.is_active, buzzer.is_active], ax, fig)
        #################################################### GRAPH DATA UPDATES ################################3

        ######### ACTIVATE BUZZER HERE (off for sanity)
        #buzzer.on()

        data_list = [[],[],[],[]]   #### EMPTY DATA SETS
        RA_list = []                #### DEFINES / CLEARS THE ROLLING AVERAGE LIST
        time_list = []              #### LIST OF TIMES FOR THE GRAPH 

        above_threshold = False     #### USED FOR ROLLING AVERAGE CHECKING
        time_pressed = 0            #### USED TO DETECT IF 3 MAIN FORCE SENSORS ARE HELD FOR 3+ SECONDS

        ########### While the gate isn't --- program halts until the button is pressed and gate opens
        while gate_open == False:
            data_list[3] = update_list(data_list[3], FSR_list[3])
            time_list = generate_time_list(len(data_list[3]))
            lines[3].set_xdata(time_list)
            lines[3].set_ydata(data_list[3])
        
            ############# Check the force sensor
            try:
                if button_sensor.force_raw() > FORCE_THRESHOLD:
                    gate_open = True
                    green_led.off()
                    #buzzer.off()
                    gate.open(dc_motor, open=True)
            except:
                print("Error opening the gate")

            ######## MATPLOTLIB ########
            plt.pause(LOOP_DELAY) 
            #################################################### GRAPH DATA UPDATES ################################3
            update_led_bars([int(red_led.is_active),int(green_led.is_active)], ax, fig)
            update_other_outputs([int(servo.is_active), int(dc_motor.is_active), int(buzzer.is_active)], ax, fig)
            #################################################### GRAPH DATA UPDATES ################################3

        #################################################### GRAPH DATA UPDATES ################################3
        update_led_bars([int(red_led.is_active),int(green_led.is_active)], ax, fig)
        update_other_outputs([int(servo.is_active), int(dc_motor.is_active), int(buzzer.is_active)], ax, fig)
        #################################################### GRAPH DATA UPDATES ################################3

        ###### Begin calculating the rolling average of FSRS
        ## Incorporate rolling average code here.

        data_list[3].clear()
        time_list.clear()
        while above_threshold != True:

            ##### RA IS THE SAME AS ROLLING AVERAGE
            RA_list.clear() ### RESETS ROLLING AVERAGE LIST
            for i in range(3):
                data_list[i] = update_list(data_list[i], FSR_list[i])
                average = FSR_rolling_average(data_list[i])
                RA_list.append(average) ##REAPPENDS ROLLING AVERAGE LIST
            data_list[3] = update_list(data_list[3], FSR_list[3])
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


            ##############################
            #### Matplotlib functions ####
            ##############################
            for i in range(3):
                lines[i].set_xdata(time_list)
                lines[i].set_ydata(data_list[i])
                ax[i,0].set_xlabel(f"Relative Time (s) | Rolling Average {i} = {RA_list[i]}", fontweight="bold")
                ax[i,0].relim()  
                fig.suptitle(f"Sensor and Output Device Data | Press time is {round(time_pressed,2)} s")

            plt.pause(LOOP_DELAY) 
            rv.time_passed += LOOP_DELAY
            #################################################### GRAPH DATA UPDATES ################################3
            update_led_bars([int(red_led.is_active),int(green_led.is_active)], ax, fig)
            update_other_outputs([int(servo.is_active), int(dc_motor.is_active), int(buzzer.is_active)], ax, fig)
            #################################################### GRAPH DATA UPDATES ################################3


        ##### BEGIN INJECTION HERE
        servo.value = inject_amount(doses_administered, int(dosage_amount))
        plt.pause(1)
        servo.detach()  ## to avoid jittering
        force_list = []  ## checks if user was still holding in proper position
        for i in range(3):
            force_list.append(FSR_list[i].force_raw())
        if force_list[0] > FORCE_THRESHOLD and force_list[1] > FORCE_THRESHOLD and force_list[2] > FORCE_THRESHOLD:
            print('delivery successful')
        else:
            print('potential incompletion in delivery')
        
        

        #################################################### GRAPH DATA UPDATES ################################3
        update_led_bars([int(red_led.is_active),int(green_led.is_active)], ax, fig)
        update_other_outputs([int(servo.is_active), int(dc_motor.is_active), int(buzzer.is_active)], ax, fig)
        #################################################### GRAPH DATA UPDATES ################################3

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

        #################################################### GRAPH DATA UPDATES ################################3
        update_led_bars([int(red_led.is_active),int(green_led.is_active)], ax, fig)
        update_other_outputs([int(servo.is_active), int(dc_motor.is_active), int(buzzer.is_active)], ax, fig)
        #################################################### GRAPH DATA UPDATES ################################3

        plt.pause(dosage_period) ### Waits for dosage period.

    #### End of autoinjector use - needs refill now.
    servo.min()  ## resets linear actuator position
    plt.pause(1)
    servo.detach()
    plt.ioff()
    plt.show()
     

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
    time_list = []
    element = LOOP_DELAY * -1*n
    for i in range(n):
        time_list.append(element)
        element += LOOP_DELAY
    return time_list




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


### updates the graph of the other outputs
def update_other_outputs(data, ax, fig):
    labels_graph_1 = ['Servo Motor', 'DC Motor', 'Buzzer']
    bar_colors = ['tab:blue', 'tab:purple', 'tab:red']
    ax[1,1].clear()
    ax[1,1].bar(labels_graph_1, data, color = bar_colors)[0] 

### CALCULATES SEVRO MOTOR PUSH DISTANCE
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / injection.CONVER_CONSTANT)*(2/1.7))-1
  return distance


