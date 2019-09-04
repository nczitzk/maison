import config
from utils import judge
from cache import queue, write_database

import re
import time
import json
import base64
from threading import Timer
import paho.mqtt.client as mqtt

state_client = mqtt.Client(config.client_name+"_state")
command_client = mqtt.Client(config.client_name+"_command")


def issue_command(devEUI, command, client_type="tx"):
    """
    To issue command through MQTT client.publish

    :param  devEUI :int    -- devEUI of the device
    :param  command:string -- command compiled by command_handler
    """
    # To encode the command with Base64.
    command = base64.b64encode(command.encode()).decode("utf-8")
    data = {
        "reference": "test",
        "confirmed": False,
        "fPort": 10,
        "data": command
    }
    command_client.publish("application/{applicationId}/device/{devEUI}/{client_type}".format(
        applicationId=config.applicationId, devEUI=devEUI, client_type=client_type), json.dumps(data), qos=1)


def parse_data(devEUI, data):
    """
    To fetch messages devices of interests
    and store info into caches for further reading.

    :param  devEUI:string -- devEUI of the device
    :param  data  :string -- data extracted from message json
    """
    # To decode data with Base64.
    data = base64.b64decode(data).decode("utf-8")

    # To deconstruct data into parts.
    parts = data.split("_")
    parts_len = len(parts)

    # More than one command are not allowed.
    if parts_len < 3 or parts_len > 4:
        issue_command(devEUI, "invalid message data: {}".format(data))
        return

    device, number, value = parts[0], int(parts[1]), parts[2]
    # "state" is ignored (see readme/command_code or readme/state_code)
    if parts_len is 3:
        key = "state"
    else:
        key, value = parts[2], parts[3]
    if not judge(device, number):
        issue_command(
            devEUI, "\"{}_{}\" does not exist".format(device, number))
        return
    if key not in config.keys[device]:
        issue_command(
            devEUI, "devices \"{}\" have no key \"{}\"".format(device, key))
        return
    if value not in config.keys[device][key]:
        issue_command(
            devEUI, "value \"{}\" is not included in key \"{}\" of devices \"{}\":".format(value, key, device) +
            ", ".join(config.keys[device][key]))
        return
    # To print for debug
    print("RECEIVED : {}_{}".format(device, number), key, value)
    write_database(device, number, devEUI, key, value)


def on_connect(client_type):
    def connect_callback(client, userdata, flags, rc):
        client.subscribe(
            "application/{applicationId}/device/+/{client_type}".format(
                applicationId=config.applicationId, client_type=client_type), qos=1)
    return connect_callback


def on_message(client, userdata, message):
    devEUI = message.topic.split('/')[3]
    parse_data(devEUI, json.loads(message.payload.decode("utf-8"))["data"])


def init(client_type):
    def client_init():
        # "tx" refers to downlink topics
        # "rx" refers to uplink topics
        client = state_client if client_type is "rx" else command_client
        client.on_connect = on_connect(client_type)
        if client_type is "rx":
            client.on_message = on_message
        client.connect(config.broker_host)
        client.loop_forever()
    return client_init


def run_cron(interval=3):
    """
    Polling to match ready-to-go cron jobs

    :param  interval:int -- time interval for one cron thread
    """
    now = time.strftime("%Y-%m-%d %H:%M:%S %w",
                        time.localtime(time.time()))
    for time_regex in queue.keys():
        if re.match(r""+time_regex, now):
            devEUI, command = queue.hmget(time_regex, "devEUI", "command")
            issue_command(devEUI, command)
            print("CRON     :", command)

            # To release space for checked cron jobs
            if re.match(r"(\d{4}-\d{1,2}-\d{1,2}\s\d{1,2}:\d{1,2}:\d{1,2}\s\w{3})", now):
                queue.delete(now)
    cron_thread = Timer(1, run_cron)
    cron_thread.start()
    time.sleep(interval)
    cron_thread.cancel()
