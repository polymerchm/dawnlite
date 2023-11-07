from dawnlite import app
from dawnlite import comm
import time
from dawnlite.enums import StatusLightMessage as MSG

# send a heartbeat request

led_queue = app.config['STATUS_LIGHT_QUEUE_KEY'] 

comm.send_message(app, MSG.HEARTBEAT, led_queue)
for i in range(0,5):
    print('...heartbeat')
    time.sleep(2)
time.sleep(5)
print("pulse_2")
comm.send_message(app, MSG.PULSE_2, led_queue)
time.sleep( 10)
print("pulse_6")
comm.send_message(app, MSG.PULSE_6, led_queue)
time.sleep(10)
print("done")





