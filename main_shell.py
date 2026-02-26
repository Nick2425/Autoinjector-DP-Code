import create_objects
import gate
import rolling_average as rv
from sensor_library import *
import injection

### Defines Global Constants
DATA_POINT_DELAY = 0.5
FORCE_THRESHOLD = 100
HOLD_TIME = 3
SYRINGE_VOLUME = 10 

def main(time_between_doses = 0):
    green_led = create_objects.GREEN_LED
    red_led = create_objects.RED_LED
    buzzer = create_objects.BUZZER
    dc_motor = create_objects.DC_MOTOR
    servo = create_objects.SERVO
    button_sensor = create_objects.FSR
    servo.detach()

    ### Doctor inputs amount of medication per delivery & length of wait time in between deliveries
    medication_volume_per_delivery = 0
    if time_between_doses == 0:
        try: 
            time_between_doses = float(input("Enter dosage period: "))    
        except:
            print("Error: Enter a number for the dosage period!")
            main()
            return 0
    try:
        medication_volume_per_delivery = input("Enter the dosage amount in mL: ")
        if str(int(medication_volume_per_delivery)) != medication_volume_per_delivery:
            print("Error: Enter an integer value for the dosage amount!")
            main(time_between_doses)
            return 0
    except:
        print("Error: Enter an integer value for the dosage amount!")
        main(time_between_doses)
        return 0
    
    medication_volume_per_delivery = int(medication_volume_per_delivery)
    time_between_doses = int(time_between_doses)
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3, button_sensor]  ## organizes the force sensing resistors *FSR*
    doses_delivered = 0
    total_delivery_count = SYRINGE_VOLUME / medication_volume_per_delivery
    while doses_delivered < total_delivery_count:
        print_outputs()  ## prints all outputs after each device status update
        red_led.off()
        is_sliding_cover_open = False
        green_led.on()
        buzzer.on()
        time.sleep(0.4)
        print_outputs(True)
        buzzer.off()
        print_outputs(True)
        raw_force_values = [[0],[0],[0]] 
        rolling_average_list = [0,0,0]                   
        contact_time = 0            
        while is_sliding_cover_open == False:
            print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()])
            try:
                if button_sensor.force_raw() > FORCE_THRESHOLD:
                    is_sliding_cover_open = True
                    green_led.off()
                    dc_motor.forward(speed=gate.SPEED)
                    print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()])
                    time.sleep(gate.TIME)
                    dc_motor.stop()
                    print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()])
            except Exception as e:   ### Accounts for potential errors in DC Motor movement including inability to rotate due to a blockage
                print(f"An unexpected error has occurred: {e}")
            time.sleep(DATA_POINT_DELAY)
        ### code below compares rolling force averages to threshold force & tracks contact time between injector and dock
        is_rolling_average_above_threshold = False
        while is_rolling_average_above_threshold != True:
            for i in range(3):
                print(i)
                raw_force_values[i] = rv.update_list(raw_force_values[i], FSR_list[i])
                rolling_average_list[i] = rv.FSR_rolling_average(raw_force_values[i])
            print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()], contact_time)
            if rolling_average_list[0] != None and rolling_average_list[1] != None and rolling_average_list[2] != None:
                if rolling_average_list[0] > FORCE_THRESHOLD and rolling_average_list[1] > FORCE_THRESHOLD and rolling_average_list[2] > FORCE_THRESHOLD: 
                    contact_time += DATA_POINT_DELAY
                    if contact_time > HOLD_TIME:                                                                   
                        is_rolling_average_above_threshold = True 
                        break                                                                                      
                else:                           
                    if contact_time > 0:        
                        contact_time = 0        
            time.sleep(DATA_POINT_DELAY) 
            rv.time_passed += DATA_POINT_DELAY

        ### code below begins delivery of medication
        servo.value = inject_amount(doses_delivered, medication_volume_per_delivery)
        print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()], contact_time)
        time.sleep(1)
        servo.detach()  
        print_outputs(True, rolling_average_list, [raw_force_values[0][-1], raw_force_values[1][-1], raw_force_values[2][-1], button_sensor.force_raw()], contact_time)
        ### code below checks whether the user maintained injector-dock contact for the entire delivery
        check_raw_force_list = []  
        for i in range(3):
            check_raw_force_list.append(FSR_list[i].force_raw())
        if not(check_raw_force_list[0] > FORCE_THRESHOLD and check_raw_force_list[1] > FORCE_THRESHOLD and check_raw_force_list[2] > FORCE_THRESHOLD):
            print('Potential incompletion in delivery')
        check_raw_force_list.append(button_sensor.force_raw()) 
        print_outputs(True, rolling_average_list, check_raw_force_list, contact_time)
        time.sleep(3)  ## gives user time to remove injector from the dock before the cover closes
        try:
            dc_motor.backward(speed=gate.SPEED)
            print_outputs(True, rolling_average_list, check_raw_force_list_2, contact_time)
            time.sleep(gate.TIME)
            dc_motor.stop()
            print_outputs(True, rolling_average_list, check_raw_force_list_2, contact_time)
        except Exception as e: ### Accounts for potential errors in DC Motor movement including inability to rotate when injector is still in contact with the dock
            print(f"An unexpected error occured: {e}")
        finally:
            pass
        doses_delivered += 1
        red_led.on()
        print_outputs(True, rolling_average_list, check_raw_force_list_2, contact_time)
        time.sleep(time_between_doses)  
    ### code below resets the device once all meedication in the injector has been delivered
    servo.min()  ## resets syringe push position 
    time.sleep(1)  ## gives the servo motor time to process
    servo.detach()




### CALCULATES AND RETURNS THE POSITION THAT THE SERVO MOTOR MUST BE SET TO BASED ON CURRENT DOSAGE COUNT
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / injection.CONVER_CONSTANT)*(2/1.7))-1
  return distance

### PRINTS THE OUTPUTS OF THE PROGRAM IN AN ORDERED FASHION
def print_outputs(pass_title = False, rolling_average_list = [None,None,None], force_raw_list = [None,None,None,None], contact_time = 0):
    if pass_title != True:
        titles = ["Red LED", 
                  "Green LED", 
                  "Buzzer", 
                  "FSR 1 (raw)", 
                  "FSR 1 (avg)", 
                  "FSR 2 (raw)", 
                  "FSR 2 (avg)", 
                  "FSR 3 (raw)", 
                  "FSR 3 (avg)", 
                  "FSR 4 (raw)", 
                  "Time Pressed", 
                  "Servo Motor", 
                  "DC Motor"]
        string = ""
        for i in titles:
            string += f"{i:<13}"
        print(string)
    data = [on_off_mapping(create_objects.RED_LED.is_active), 
            on_off_mapping(create_objects.GREEN_LED.is_active), 
            on_off_mapping(create_objects.BUZZER.is_active), 
            force_raw_list[0],
            rolling_average_list[0], 
            force_raw_list[1],
            rolling_average_list[1], 
            force_raw_list[2],
            rolling_average_list[2], 
            force_raw_list[3],
            round(contact_time,2),
            rotate_mapping(create_objects.SERVO.is_active),
            rotate_mapping(create_objects.DC_MOTOR.is_active)]
    string = ""
    for i in data:
        string += f"{str(i):<13}"
    print(string)


### THIS CONVERTS TRUE OR FALSE STATEMENTS INTO ON OR OFF STRINGS FOR OUR LEDS
def on_off_mapping(active):
    if active == True:
        return "On"
    else:
        return "Off"
    
### THIS CONVERTS TRUE OR FALSE STATEMENTS INTO ROTATING OR OFF STRINGS FOR OUR MOTORS
def rotate_mapping(active):
    if active == True:
        return "Rotating"
    else:
        return "Off"
