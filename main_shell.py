import create_objects
import gate
import rolling_average as rv
from sensor_library import *
import injection

### Defines Global Constants
LOOP_DELAY = 0.5
FORCE_THRESHOLD = 100
HOLD_TIME = 3
SYRINGE_VOLUME = 10 

def main(dosage_period = 0):
    green_led = create_objects.GREEN_LED
    red_led = create_objects.RED_LED
    buzzer = create_objects.BUZZER
    dc_motor = create_objects.DC_MOTOR
    servo = create_objects.SERVO
    button_sensor = create_objects.FSR
    servo.detach()

    ### Doctor inputs amount of medication per delivery & length of wait time in between deliveries
    dosage_amount = 0
    if dosage_period == 0:
        try: 
            dosage_period = float(input("Enter dosage period: "))    
        except:
            print("Error: Enter a number for the dosage period!")
            main()
            return 0
    try:
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
    dosage_amount = int(dosage_amount)
    dosage_period = int(dosage_period)
    FSR_list = [rv.FSR1, rv.FSR2, rv.FSR3, button_sensor]
    doses_administered = 0
    dosage_count = SYRINGE_VOLUME / dosage_amount
    while doses_administered < dosage_count:
        print_outputs()
        red_led.off()
        gate_open = False
        green_led.on()
        buzzer.on()
        time.sleep(0.4)
        print_outputs(True)
        buzzer.off()
        print_outputs(True)
        data_list = [[0],[0],[0]] 
        RA_list = [0,0,0]               
        above_threshold = False     
        time_pressed = 0            
        while gate_open == False:
            print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()])
            try:
                if button_sensor.force_raw() > FORCE_THRESHOLD:
                    gate_open = True
                    green_led.off()
                    dc_motor.forward(speed=gate.SPEED)
                    print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()])
                    time.sleep(gate.TIME)
                    dc_motor.stop()
                    print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()])
            except:
                print("Error opening the gate")
            time.sleep(LOOP_DELAY) 
        while above_threshold != True:
            i = 0
            while i < 3:
                print(i)
                data_list[i] = rv.update_list(data_list[i], FSR_list[i])
                RA_list[i] = rv.FSR_rolling_average(data_list[i])
                i+=1
            print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()], time_pressed)
            if RA_list[0] != None and RA_list[1] != None and RA_list[2] != None:
                if RA_list[0] > FORCE_THRESHOLD and RA_list[1] > FORCE_THRESHOLD and RA_list[2] > FORCE_THRESHOLD: 
                    time_pressed += LOOP_DELAY
                    if time_pressed > HOLD_TIME:                                                                   
                        above_threshold = True 
                        break                                                                                      
                else:                           
                    if time_pressed > 0:        
                        time_pressed = 0        
            time.sleep(LOOP_DELAY) 
            rv.time_passed += LOOP_DELAY

        ##### BEGIN INJECTION HERE

        servo.value = inject_amount(doses_administered, int(dosage_amount))
        print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()], time_pressed)
        time.sleep(1)
        servo.detach()  
        print_outputs(True, RA_list, [data_list[0][-1], data_list[1][-1], data_list[2][-1], button_sensor.force_raw()], time_pressed)
        force_list = []  
        for i in range(3):
            force_list.append(FSR_list[i].force_raw())
        if force_list[0] > FORCE_THRESHOLD and force_list[1] > FORCE_THRESHOLD and force_list[2] > FORCE_THRESHOLD:
            pass
        else:
            print('potential incompletion in delivery')
        force_list_2 = []
        for i in force_list:
            force_list_2.append(i)
        force_list_2.append(button_sensor.force_raw()) 
        print_outputs(True, RA_list, force_list_2, time_pressed)
        time.sleep(5)
        try:
            dc_motor.backward(speed=gate.SPEED)
            print_outputs(True, RA_list, force_list_2, time_pressed)
            time.sleep(gate.TIME)
            dc_motor.stop()
            print_outputs(True, RA_list, force_list_2, time_pressed)
        except:
            print("Error closing the gate")
        doses_administered += 1
        red_led.on()
        print_outputs(True, RA_list, force_list_2, time_pressed)
        time.sleep(dosage_period) 
    servo.min()  
    time.sleep(1)
    servo.detach()




### CALCULATES AND RETURNS THE POSITION THAT THE SERVO MOTOR MUST BE SET TO BASED ON CURRENT DOSAGE COUNT
def inject_amount(count, dosage):
  current_amount = (count+1) * dosage
  distance = ((current_amount / injection.CONVER_CONSTANT)*(2/1.7))-1
  return distance

### PRINTS THE OUTPUTS OF THE PROGRAM IN AN ORDERED FASHION
def print_outputs(pass_title = False, rolling_average_list = ["N/A","N/A","N/A"], force_raw_list = ["N/A","N/A","N/A","N/A"], time_pressed = 0):
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
            round(time_pressed,2),
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
