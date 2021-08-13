# Intro

This repo is inended to contain a basic source code to manage data from
meshtastic devices using another meshtastic device.

The received data will be sent to a mqtt server, which will manage the data.

## Meshtastic python Github page

https://github.com/meshtastic/Meshtastic-python/tree/master

## Install dependencies

python3 -m pip install -r requirements.txt

## Create a startup script

You can pick the file `main.sh.example` to understand how to customize
your environment variables.

```bash
STATION_MQTT_HOST=meshtastic_mqtt # the hostname for mqtt server
STATION_MQTT_PORT=1883 # the port for mqtt server
STATION_MQTT_IN_TOPIC=input_data # the input topic for mqtt server
STATION_GET_NODES_INTERVAL=10 # freq. to get nodes data, for periodic version only
```