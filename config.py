import os
import json
import toml

path = os.path.dirname(os.path.abspath(__file__))
filename = os.path.join(path, "config.toml")

if not os.path.exists(filename):
    example = """app_host = "localhost"
app_port = 2019

# MQTT client name

client_name = "maison_client"

[Broker]

# You need a MQTT broker to handle MQTT service.
# Here are some public brokers for testing.

# broker_host = "test.mosquitto.org"
# broker_host = "broker.hivemq.com"
broker_host = "iot.eclipse.org"
broker_port = 1883

# Enable InfluxDB to make sure storage works.

[InfluxDB]

database_host = "localhost"
database_port = 8086
database_username = "maison_user"
database_password = "maison"
database_name = "maison_database"

# Enable Redis to support cron jobs.

[Redis]

queue_host = "localhost"
queue_port = 6379
queue_id = 0

# Each devices should have a devEUI for identifying,
# if you want to connect with LoRa server.

[devEUI]

"light_1" = 3634374710300059
"light_2" = 3634374710300058
"light_3" = 3634374710300057
"light_4" = 3634374710300056
"light_5" = 3634374710300055
"light_6" = 3634374710300054
"light_7" = 3634374710300053
"fan_1" = 3634374710300052
"fan_2" = 3634374710300051
"curtain_1" = 3634374710300049
"curtain_2" = 3634374710300048
"curtain_3" = 3634374710300047
"ac_27" = 3634374710300046
"ac_33" = 3634374710300045
"ac_44" = 3634374710300044
"ac_62" = 3634374710300043

[device]

# "_keys" is for verifying whether the keys and values is valid or not.

"_keys" = '''
{
    "light": {"state": ["off", "on"]},
    "fan": {"speed": ["0", "1", "2", "3"]},
    "curtain": {"state": ["off", "on", "pause"]},
    "ac": {
        "state": ["off", "on"],
        "mode": ["auto", "cool", "dry", "fan", "heat"],
        "speed": ["auto", "low", "high"],
        "swing": ["auto", "manual"],
        "temp": ["16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26", "27", "28", "29", "30"]
    }
}'''

[id]

# To shorten the device type to given id

"light"= "1"
"fan" = "2"
"curtain" = "3"
"ac" = "4"

[value]

"on" = "0"
"off" = "1"
"pause" = "2"

# Each scenario triggers different actions.
# You should define actions when the mode is "on" as well as "off".

[scenario]

"classmode" = '''
{
    "on": {
        "light_1": {"state": "on"},
        "fan_1": {"speed": "1"}
    },
    "off": {
        "light_1": {"state": "off"}
    }
}'''

"smartmode" = '''
{
    "on": {
        "light_1": {"state": "on"},
        "fan_1": {"speed": "2"},
        "ac_27": {
            "state": "on",
            "mode": "auto"
        }
    },
    "off": {}
}'''"""
    with open(filename, 'a+', encoding='utf-8') as f:
        toml.dump(toml.loads(example), f)


configs = toml.load(filename)

configs.setdefault("devices", {})
devEUIs = configs["devEUI"]

for device in devEUIs.keys():
    (device_type, device_num) = device.split("_")
    configs["devices"].setdefault(device_type, [])
    configs["devices"][device_type].append(device_num)
