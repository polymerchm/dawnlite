from gpiozero import Button
import time
button = Button(20,None,True)
while True:
    if button.is_pressed:
        print("Button is pressed")
    else:
        print("Button is not pressed")
    time.sleep(0.1)

