# bluetoothle_sensor

A brief history of how this came about

Actually i wanted a node-red plugin for govee.
I tried to use this:
https://github.com/johnmckerrell/node-red-contrib-govee-bt-client
but always ran into the problems with @abandonware/noble (node red crash)

I tried node-red-contrib-generic-ble but the connection kept getting lost.

I tried https://github.com/w1gx/govee-ble-scanner but it blocks the bluetooth device and so i could not retrieve the data from the xiaomi.

I have found https://github.com/wcbonner/GoveeBTTempLogger but I did not want mrtg.

I have tried homeassistant ble_monitor without success (version hassle) and i use homeassitant only as a dashboard.
https://github.com/custom-components/ble_monitor

And some other projects I tried briefly.

I came to the conclusion i need a very, simple solution. A script that queries the data and writes it "somewhere". 

On https://github.com/TheCellule/python-bleson i failed on xiaomi with ServiceData

I found a wonderfull project about result processing https://github.com/Ernst79/bleparser, it is a decoupling from the homeassistant componente. And I've stumbled across https://github.com/frawau/aioblescan before, but couldn't do anything with the results here at first.
But just throwing the raw data into bleparser and.... wauuuh cool, that was easy.

The bluetooth device is not blocked! Unfortunately, after a connection no more messages come, the problem was known:
https://github.com/frawau/aioblescan/issues/9 but I could not see how to solve this. I found a workaround with ALARM signal. And a little bit of mqtt complexity I added now, but so the detected data is simply written to a mqtt topic, the further processing I do in node-red.

pip3 install -r requirements.txt 

. venv/bin/activate

#maybe change:

#broker = "localhost"

#port = 1883

#topic = "bluetoothle_sensor"

python3 monitor.py


