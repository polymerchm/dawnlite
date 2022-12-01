import subprocess


def getWiFiList():
    result = subprocess.run(['sudo', r'/home/pi/Programming/dawn_lite/scanWLAN.sh'],capture_output=True)
    if result.returncode != 0:
        wifiList = []
    else:
        tokens = list(set([s.strip().split(":")[1].replace('"','')  for s in result.stdout.decode("utf-8").split('\n') if len(s.strip().split(":")) == 2]))

        wifiList = sorted([token for token in tokens if len(token) > 0  and not token.startswith('\x00') ])

    return wifiList
