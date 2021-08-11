#!/usr/bin/env python3

import asyncio
import aioblescan as aiobs
from bleparser import BleParser
import paho.mqtt.client as paho
import json
import signal

#data_string = "043e2502010000219335342d5819020106151695fe5020aa01da219335342d580d1004fe004802c4"
#data = b'\x04>%\x02\x01\x00\x00\x00G\xdc\xa8eL\x19\x02\x01\x06\x15\x16\x95\xfeP \xaa\x01\xcf\x00G\xdc\xa8eL\r\x10\x04\xf4\x00\\\x02\x9f'
#data_string = str(data_string)
#print (data_string)
#data = bytes(bytearray.fromhex(data_string))

def alarm_handler(signum, frame):
    print("Event timeout")
    raise Exception("Event_Timeout")

signal.signal(signal.SIGALRM, alarm_handler)

broker = "localhost"
port = 1883
topic = "bluetoothle_sensor"

def on_publish(client,userdata,result):
    print("data published \n")
    pass

mqtt_client = paho.Client("control1")
mqtt_client.on_publish = on_publish
mqtt_client.connect(broker,port)

def publish(data):
    ret = mqtt_client.publish(topic,json.dumps(data))


def ble_parse(data):

    ble_parser = BleParser()
    try:
        sensor_msg, tracker_msg = ble_parser.parse_data(data)
        print(sensor_msg, tracker_msg)
        if sensor_msg is not None:
            return sensor_msg
    except TypeError:
	    pass # 'NoneType' object is not subscriptable

def process_raw(data):

    signal.alarm(10)

    ev = aiobs.HCI_Event()
    xx = ev.decode(data)

    raw_data = ev.raw_data
    print("Raw data: {}".format(raw_data))
    if raw_data is not None:
        parsed_data = ble_parse(raw_data)
        if parsed_data is not None:
            publish(parsed_data)

class eventLoop:

    def __init__(self):
        self.event_loop = asyncio.get_event_loop()
        
        self.mysocket = aiobs.create_bt_socket(0)
        
        fac = self.event_loop._create_connection_transport(
            self.mysocket, aiobs.BLEScanRequester, None, None
        )

        self.conn, self.btctrl = self.event_loop.run_until_complete(fac)
        self.btctrl.process = process_raw
        
        self.event_loop.run_until_complete(self.btctrl.send_scan_request())

if __name__ == "__main__":

    while True:
        event = eventLoop()

        try:
            
            event.event_loop.run_forever()
        except KeyboardInterrupt:
            print("keyboard interrupt")
            break
        except Exception as e:
            print("Exception", e)
        finally:
            print("closing event loop")
            event.event_loop.run_until_complete(event.btctrl.stop_scan_request())
            command = aiobs.HCI_Cmd_LE_Advertise(enable=False)
            event.event_loop.run_until_complete(event.btctrl.send_command(command))
            event.conn.close()
            #event.event_loop.close()





