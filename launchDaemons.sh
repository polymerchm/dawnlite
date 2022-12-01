#!/usr/bin/bash
source venv/bin/activate
nohup python3 -m dawnlite.daemons.button &
nohup python3 -m dawnlite.daemons.remoteControl &
nohup python3 -m dawnlite.daemons.statusLED &
nohup python3 -m dawnlite.daemon &
