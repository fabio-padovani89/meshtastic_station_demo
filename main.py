import atexit
import os
import time

from json import dumps

import meshtastic
import paho.mqtt.client as mqtt_client


class MQTTInterface:

    def __init__(self, host=None, topic=None):
        self.client = None
        self.host = host
        self.topic = topic

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print('Connected to MQTT Broker!')
            else:
                print('Failed to connect, return code %d\n', rc)

        self.client = mqtt_client.Client()
        self.client.on_connect = on_connect
        self.client.connect(self.host)
        self.client.loop_start()

    def publish(self, messages):
        self.client.publish(
            self.topic,
            dumps(messages)
        )
    
    def close(self):
        self.client.disconnect()


class Station:

    def __init__(self):
        self.interface = meshtastic.SerialInterface()
        self.current_node_info = self.interface.getMyNodeInfo()
        self.current_node_id = self.current_node_info.get('num', None)
    
    def get_nodes_info(self):
        res = []
        current_time = int(time.time())

        self.interface.showNodes()

        for node in self.interface.nodes.values():
            if node['num'] != self.current_node_id:
                pos = node.get('position', {})

                res.append({
                    'num': node.get('num'),
                    'user': node.get('user', {}),
                    'position': {
                        'latitude': pos.get('latitude'),
                        'longitude': pos.get('longitude'),
                        'time': pos.get('time'),
                    },
                    'batteryLevel': pos.get('batteryLevel'),
                    'snr': node.get('snr'),
                    'relevation_time': current_time
                })
        return res

    def close(self):
        self.interface.close()


# MQTT
mqtt = MQTTInterface(
    host=os.environ.get('STATION_MQTT_HOST'),
    topic=os.environ.get('STATION_MQTT_IN_TOPIC')
)
mqtt.connect()


# STATION
station = Station()

def handle_nodes_data():
    data = station.get_nodes_info()
    mqtt.publish(data)

def exit_procedure():
    station.close()
    mqtt.close()

if __name__ == '__main__':
    handle_nodes_data()
    atexit.register(exit_procedure)

