import wiringpi

#PIN_TO_SENSE = 14
PIN_TO_SENSE = 4

def gpio_callback_rising():
    print("GPIO_CALLBACK_RISING!")

wiringpi.wiringPiSetupGpio()
wiringpi.pinMode(PIN_TO_SENSE, wiringpi.GPIO.INPUT)
wiringpi.pullUpDnControl(PIN_TO_SENSE, wiringpi.GPIO.PUD_DOWN)
wiringpi.wiringPiISR(PIN_TO_SENSE, wiringpi.GPIO.INT_EDGE_RISING, gpio_callback_rising)

while True:
    wiringpi.delay(2000)