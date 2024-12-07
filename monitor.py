#!/usr/bin/env python3

import asyncio
import aioblescan as aiobs
from bleparser import BleParser
import paho.mqtt.client as paho
import json
import signal
from zeroconf import ServiceBrowser, Zeroconf
import time
import socket
import platform

MQTT_TOPIC = "bluetoothle_sensor"

#data_string = "043e2502010000219335342d5819020106151695fe5020aa01da219335342d580d1004fe004802c4"
#data = b'\x04>%\x02\x01\x00\x00\x00G\xdc\xa8eL\x19\x02\x01\x06\x15\x16\x95\xfeP \xaa\x01\xcf\x00G\xdc\xa8eL\r\x10\x04\xf4\x00\\\x02\x9f'
#data_string = str(data_string)
#print (data_string)
#data = bytes(bytearray.fromhex(data_string))

class zeroconfListener:

    def __init__(self):
        self.mqtt_address = None
        self.mqtt_port = None

    def remove_service(self, zeroconf, type, name):
        print("Service %s removed" % (name,))

    def add_service(self, zeroconf, type, name):
        global mqtt_address, mqtt_port
        info = zeroconf.get_service_info(type, name)
        print("Service %s added, service info: %s" % (name, info))
        for address in info.addresses:
            print("Address: %s %d" % (socket.inet_ntoa(address), info.port))
            self.mqtt_address = socket.inet_ntoa(address)
            self.mqtt_port = info.port

    def update_service(self, zeroconf, type, name):
        print ("update")

    def get_mqtt(self):
        return (self.mqtt_address, self.mqtt_port)

    def mqtt_exists(self):
        if self.mqtt_address == None or self.mqtt_port == 0:
            return False
        return True


class zeroconfMqtt:

    def __init__(self):
        self.zeroconf = Zeroconf()
        self.listener = zeroconfListener()
        self.browser = ServiceBrowser(self.zeroconf, "_mqtt._tcp.local.", self.listener)

    def get_mqtt_host(self):
        try:
            while not self.listener.mqtt_exists():
                print("no mqtt_address, mqtt_port")
                time.sleep(1)

            return self.listener.get_mqtt()
            #input("Press enter to exit...\n\n")
        finally:
            self.zeroconf.close()



def alarm_handler(signum, frame):
    print("Event timeout")
    raise Exception("Event_Timeout")

def on_publish(client,userdata,result):
    #print("data published \n")
    pass


def publish(data):
    ret = mqtt_client.publish(topic,json.dumps(data))


def ble_parse(data):

    ble_parser = BleParser()
    try:
        sensor_msg, tracker_msg = ble_parser.parse_raw_data(data)
        if sensor_msg is not None:
            #print("sensor", sensor_msg)
            #print("tracker", tracker_msg)
            return sensor_msg
    except TypeError:
	    pass # 'NoneType' object is not subscriptable

last_data = {}

def process_raw(data):

    signal.alarm(10)

    ev = aiobs.HCI_Event()
    xx = ev.decode(data)

    raw_data = ev.raw_data
    #print(f"Raw data: {raw_data}")
    if raw_data is not None:
        parsed_data = ble_parse(raw_data)
        if parsed_data is not None and "mac" in parsed_data:
            if parsed_data["mac"] in last_data:
                if last_data[parsed_data["mac"]]["time"] + 10 > time.time():
                    #print("time skipping", parsed_data)
                    return
                if (parsed_data["mac"] == last_data[parsed_data["mac"]]["data"] and
                    last_data[parsed_data["mac"]]["time"] + 60 < time.time()):
                    print("data skipping", parsed_data)
                    return
            last_data[parsed_data["mac"]] = { "data": parsed_data, "time": time.time() }
            #if "A4C138281A44" in parsed_data["mac"]:
            #    print(parsed_data)
            #    print(last_data[parsed_data["mac"]])
            print(parsed_data)
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

    signal.signal(signal.SIGALRM, alarm_handler)

    zcm = zeroconfMqtt()
    host, port = zcm.get_mqtt_host()
    print(host, port)

    topic = MQTT_TOPIC

    mqtt_client = paho.Client(f"{platform.node()}-ble-monitor")
    mqtt_client.on_publish = on_publish
    mqtt_client.connect(host,port)
    mqtt_client.loop_start()

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

    mqtt_client.loop_stop()



