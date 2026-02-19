from gpiozero import LED
import time

GREEN_LED_PIN = 21
RED_LED_PIN = 20

GREEN_LED = LED(21)
RED_LED = LED(20)

def test_led():
    GREEN_LED.on()
    time.sleep(5)
    RED_LED.on()