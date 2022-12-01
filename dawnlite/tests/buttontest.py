from dawnlite.hw.button_utils import Button

import time





def main():

    def longPress():
        button.state = 2


    def pressed():
        button.state = 1    

    button_pin = 2

    button = Button(button_pin)
    button.when_pressed = pressed
    button.when_held = longPress

    while 1:
        time.sleep(1)
        print("sleeping...", button.state, "hold_time", button.held_time, button.is_held)
        if button.state != 0:
            button.resetState()







if __name__ == "__main__":
    state = 0
    main()