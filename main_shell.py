import create_objects
import gate
import rolling_average as rv
from sensor_library import *
from gpiozero import Buzzer
from gpiozero import Motor
from gpiozero import Servo
from gpiozero import LED
import injection

LOOP_DELAY = 0.2
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

    servo.detach()

    dosage_amount = 0
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

    ############### TIME LIST DEFINITION AND FORCE SENSOR OBJECTS ################
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3, button_sensor]

    #### ESTABLISH INITIAL DOSAGE COUNT AND DOSES ADMINISTERED
    doses_administered = 0
    dosage_count = SYRINGE_VOLUME / dosage_amount


    ###### MAIN LOOP BEGINS HERE #####################
    while doses_administered < dosage_count:
        print_outputs()
        ######### initialize gate and LEDs
        red_led.off()
        gate_open = False
        green_led.on()
        
        ######### ACTIVATE BUZZER HERE (off for sanity)
        buzzer.on()
        print_outputs(True)

        data_list = [[0],[0],[0],[0]]   #### EMPTY DATA SETS
        RA_list = [0,0,0]                #### DEFINES / CLEARS THE ROLLING AVERAGE LIST

        above_threshold = False     #### USED FOR ROLLING AVERAGE CHECKING
        time_pressed = 0            #### USED TO DETECT IF 3 MAIN FORCE SENSORS ARE HELD FOR 3+ SECONDS

        ########### While the gate isn't --- program halts until the button is pressed and gate opens
        while gate_open == False:
            data_list[3] = update_list(data_list[3], FSR_list[3])
            print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], data_list[3][-1]])

            ############# Check the force sensor
            try:
                if button_sensor.force_raw() > FORCE_THRESHOLD:
                    gate_open = True
                    green_led.off()
                    buzzer.off()
                    gate.open(dc_motor, open=True)
                    print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], data_list[3][-1]])

            except:
                print("Error opening the gate")

            ######## MATPLOTLIB ########
            time.sleep(LOOP_DELAY) 

        ###### Begin calculating the rolling average of FSRS
        ## Incorporate rolling average code here.

        while above_threshold != True:

            ##### RA IS THE SAME AS ROLLING AVERAGE
            RA_list.clear() ### RESETS ROLLING AVERAGE LIST
            for i in range(3):
                data_list[i] = update_list(data_list[i], FSR_list[i])
                average = FSR_rolling_average(data_list[i])
                RA_list.append(average) ##REAPPENDS ROLLING AVERAGE LIST
            print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], data_list[3][-1]], time_pressed)
            #### Compares rolling averages and checks if they are defined or are null
            if RA_list[0] != None and RA_list[1] != None and RA_list[2] != None:
                if RA_list[0] > FORCE_THRESHOLD and RA_list[1] > FORCE_THRESHOLD and RA_list[2] > FORCE_THRESHOLD:  ### imcrements time the sensor is pushed for
                    time_pressed += LOOP_DELAY
                                                                      ### adjusts for unknown time delay
                    if time_pressed > HOLD_TIME:                                                                    ### checks if sensor is held for the total hold time
                        above_threshold = True 
                        break                                                                                       ### This exists the loop
                else:                           #### checks if person lets go and resets if necessary.
                    if time_pressed > 0:        #### Resets the hold time if the averages aren't all above 0
                        time_pressed = 0        #### which can imply that the device is in contact at the wrong angle and therefore can malfunction

            time.sleep(LOOP_DELAY) 
            rv.time_passed += LOOP_DELAY

        ##### BEGIN INJECTION HERE

        servo.value = inject_amount(doses_administered, int(dosage_amount))
        print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], data_list[3][-1]], time_pressed)
        time.sleep(1)
        servo.detach()  ## to avoid jittering
        print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], data_list[3][-1]], time_pressed)
        force_list = []  ## checks if user was still holding in proper position
        for i in range(3):
            force_list.append(FSR_list[i].force_raw())
        if force_list[0] > FORCE_THRESHOLD and force_list[1] > FORCE_THRESHOLD and force_list[2] > FORCE_THRESHOLD:
            print('delivery successful')
        else:
            print('potential incompletion in delivery')
        force_list_2 = []
        for i in force_list:
            force_list_2.append(i)
        force_list_2.append(data_list[3][-1]) 
        print_outputs(True, RA_list, force_list_2, time_pressed)

        
        ##### Grace period after injection
        time.sleep(5)
        ##### Close the gate
        try:
            create_objects.DC_MOTOR.backward(speed=gate.SPEED)
            print_outputs(True, RA_list, force_list_2, time_pressed)
            time.sleep(gate.TIME)
            create_objects.DC_MOTOR.stop()
            print_outputs(True, RA_list, force_list_2, time_pressed)
        except:
            print("Error closing the gate")


        ### Finishing the dose administration
        doses_administered += 1
        red_led.on()
        print_outputs(True, RA_list, force_list_2, time_pressed)
        time.sleep(dosage_period) ### Waits for dosage period.

    #### End of autoinjector use - needs refill now.
    servo.min()  ## resets linear actuator position
    time.sleep(1)
    servo.detach()



####### THIS UPDATES THE STORED FORCE VALUES IN THE LIST AFTER REACHING MAXIMUM CAPACITY
def update_list(inputed_list, sensor: Force_Sensing_Resistor):
    updated_list = inputed_list.copy()
    if len(updated_list) < 150: ### stores elements up to 150
        updated_list.append(sensor.force_raw())
    else:
        updated_list.pop(0)
        updated_list.append(sensor.force_raw())
    return updated_list

####### ROLLING AVERAGE CODE COPIED
def FSR_rolling_average(datalist):
  if len(datalist) < 30:
    return None
  else:
    rolling_av = sum(datalist, -30)/30 #### Returns the rolling average of the latest 30 elements.
    return round(rolling_av, 2)

### CALCULATES SEVRO MOTOR PUSH DISTANCE
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / injection.CONVER_CONSTANT)*(2/1.7))-1
  return distance

    
def print_outputs(pass_title = False, rolling_average_list = ["N/A","N/A","N/A"], force_raw_list = ["N/A","N/A","N/A","N/A"], time_pressed = 0):
    if pass_title != True:
        titles = ["Red LED", "Green LED", "Buzzer", "FSR 1 (raw)", "FSR 1 (avg)", "FSR 2 (raw)", "FSR 2 (avg)", "FSR 3 (raw)", "FSR 3 (avg)", "FSR 4 (raw)", "Servo Motor", "DC Motor"]
        string = ""
        for i in titles:
            string += f"{i:<15}"
        print(string)
    data = [on_off_mapping(create_objects.RED_LED.is_active), 
            on_off_mapping(create_objects.GREEN_LED.is_active), 
            on_off_mapping(create_objects.Buzzer.is_active), 
            force_raw_list[0],
            rolling_average_list[0], 
            force_raw_list[1],
            rolling_average_list[1], 
            force_raw_list[2],
            rolling_average_list[2], 
            force_raw_list[3],
            time_pressed,
            rotate_mapping(create_objects.SERVO.is_active),
            rotate_mapping(create_objects.DC_MOTOR.is_active)]
    string = ""
    for i in data:
        string += f"{str(i):<15}"
    print(string)


def on_off_mapping(active):
    if active == True:
        return "On"
    else:
        return "Off"
def rotate_mapping(active):
    if active == True:
        return "Rotating"
    else:
        return "Off"