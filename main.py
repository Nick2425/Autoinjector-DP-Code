import create_objects
import time
import gate

LOOP_DELAY = 0.05
FORCE_THRESHOLD = 0
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