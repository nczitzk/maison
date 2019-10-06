<p align="center">
    <a href="https://github.com/nczitzk/maison" target="_blank">
        <img width="200" src="https://github.com/nczitzk/maison/wiki/maison.png" alt="maison-logo">
    </a>
</p>

<p align="center">
    <a href="https://github.com/nczitzk/maison/blob/master/LICENSE" target="_blank">
        <img src="https://img.shields.io/github/license/nczitzk/maison.svg?style=flat-square" alt="maison-license">
    </a>
    <a href="https://github.com/nczitzk/maison" target="_blank">
        <img src="https://img.shields.io/github/languages/code-size/nczitzk/maison.svg?style=flat-square" alt="maison-size">
    </a>
</p>

__Maison__ /mεzɔ̃/ is a highly customized control center of smart homes and also a light-weight solution for managing several household appliances.

One configuration TOML file is all Maison need. To feed it with commands to appliances or states of devices using MQTT (Message Queuing Telemetry Transport) from LoRa server or other MQTT sources, Maison will issue commands to certain devices and stores changes on states of devices in the database for monitoring in real time.

Also, Maison provides couples of HTTP APIs for client to request so that you can connect smart home APP and smart household appliances seamlessly and painlessly. You can create cron jobs to update devices settings periodically, which is so handy that you only have to add a timestamp in request JSON.

It, at first, was a tiny project which is to build some certain smart classrooms for new campus, working with fixed number and types of devices. As development goes on, making it a more general solution came up in my mind. So here is it.

## Get Started

Install InfluxDB for storage and run it at localhost:8086. See [InfluxDB Documentation](https://docs.influxdata.com/influxdb/v1.7)

Install Redis for cron jobs and run it at localhost:6379. See [Redis Documentation](https://redis.io/documentation)

The both host and port of databases above can be modified in the configuration file. Then, run

```
pip install -r requirements.txt
python main.py
```

Now, the MQTT broker and Maison APIs are working. You can manipulate the appliances by accessing APIs or connecting to your LoRa Server or just using bare MQTT client for testing.

### API

POST the following JSON data to http://localhost:2019/command/light/1/

```
{
    "state": "on"
}
```

### MQTT client

You need a MQTT client to mime LoRa Server actions. [Eclipse Mosquitto](https://mosquitto.org/) is a good choice. If you prefer one with graphic interface, [MQTTfx](http://www.mqttfx.org/) might be what you want. Try subscribing "application/1/device/light/rx" and then publish the following JSON to the topic.

```
{
    "data": "{\"state\":\"on\"}"
}
```

### LoRa Server

See chapter about MQTT integration in [Lora Server Documentation](https://www.loraserver.io/lora-app-server/integrate/sending-receiving/mqtt/)

If everything goes well, your light_1 should be on.

Enjoy :P

## Configuration File

[An example configuration file](https://github.com/nczitzk/maison/blob/master/config.toml) is offered. All devices properties and commands or statesinformation can be customized.

## Use HTTP APIs

- [/command](https://github.com/nczitzk/maison/wiki/command) (cron jobs supported)
- [/state](https://github.com/nczitzk/maison/wiki/state)

## Message Data Format

- [Command Code](https://github.com/nczitzk/maison/wiki/command_code)
- [State Code](https://github.com/nczitzk/maison/wiki/state_code)

## License

[GNU Affero General Public License v3.0](https://github.com/nczitzk/maison/blob/master/LICENSE)