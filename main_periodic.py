import atexit
import os
import time

from json import dumps
from threading import Timer

import meshtastic
import paho.mqtt.client as mqtt_client


class PeriodicTask(object):
    def __init__(self, interval, callback, daemon=True, **kwargs):
        self.interval = interval
        self.callback = callback
        self.daemon   = daemon
        self.kwargs   = kwargs

    def run(self):
        self.callback(**self.kwargs)
        t = Timer(self.interval, self.run)
        t.daemon = self.daemon
        t.start()


class MQTTInterface:
    default_port = 1883

    def __init__(self, host=None, port=None, topic=None):
        self.client = None
        self.host = host
        self.port = int(port) if port is not None else self.default_port
        self.topic = topic

    def connect(self):
        def on_connect(client, userdata, flags, rc):
            if rc == 0:
                print('Connected to MQTT Broker!')
            else:
                print('Failed to connect, return code %d\n', rc)

        self.client = mqtt_client.Client()
        self.client.on_connect = on_connect
        self.client.connect(self.host, port=self.port)
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
    port=os.environ.get('STATION_MQTT_PORT'),
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
    task_nodes_data = PeriodicTask(
        interval=int(os.environ.get('STATION_GET_NODES_INTERVAL')),
        callback=handle_nodes_data,
        daemon=False
    )
    task_nodes_data.run()

    atexit.register(exit_procedure)

