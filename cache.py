from config import configs
from utils import get_timestamp

import json
import redis
from influxdb import InfluxDBClient

keys = json.loads(configs["device"]["_keys"])

client = InfluxDBClient(configs["database_host"], configs["database_port"],
                        configs["database_username"], configs["database_password"], configs["database_name"])

pool = redis.ConnectionPool(host=configs["queue_host"],
                            port=configs["queue_port"], db=configs["queue_id"], decode_responses=True)
queue = redis.Redis(connection_pool=pool)


def write_database(device, number, devEUI, key, value):
    """
    To write new states to database.

    :param  device:string -- device name (eg. light, fan...)
    :param  number:int    -- device number (eg. 0 for all, 1 for No.1...)
    :param  devEUI:int    -- devEUI of the device
    :param  key:string    -- key of the device
    :param  value:string  -- value of the key
    """
    data = {
        "time": get_timestamp("now", "ms"),
        "tags": {"devEUI": devEUI},
        "fields": {key: value}
    }

    # If commands acting on all devices of same type,
    # then push them into datas.
    if number is 0:
        for n in configs["devices"][device]:
            datas = []
            data["tags"] = {
                "devEUI": configs["devEUI"]["{}_{}".format(device, n)]}
            data["measurement"] = "{}_{}".format(device, n)
            datas.append(data)
            print("WRITE    : ", data)
            client.write_points(datas)
    else:
        datas = []
        data["tags"] = {
            "devEUI": configs["devEUI"]["{}_{}".format(device, number)]}
        data["measurement"] = "{}_{}".format(device, number)
        datas.append(data)
        print("WRITE    : ", data)
        client.write_points(datas, time_precision="ms")


def query_database(device, number, form):
    """
    To make simple Structive Query Language statements from couples of arguments
    and fetch latest states or that recorded in history.

    :param  device:string -- device name (eg. light, fan...)
    :param  number:int    -- device number (eg. 0 for all, 1 for No.1...)
    :param  form  :json   -- argument form (see readme/state)
    :return string
    """
    # defaults
    selects = keys[device].keys()
    where = query = ""
    time_reverse = "ORDER BY time DESC"
    timezone = "Asia/Shanghai"
    limit = 1

    for (key, value) in form.items():
        if key == "states":
            selects = value.split(",")
        if key == "where":
            where = value
        if key == "time_reverse" and value == False:
            time_reverse = ""
        if key == "limit":
            if value >= 1 and value <= 50:
                limit = value
        if key == "timezone":
            timezone = value

    for select in selects:
        query += "SELECT {select} FROM {device}_{number}{where} {time_reverse} LIMIT {limit} TZ('{timezone}');".format(
            select=select, device=device, number=number, where="" if not where else " where {}".format(
                where), time_reverse=time_reverse, limit=limit, timezone=timezone)
    return client.query(query)


def add_cron(time, devEUI, command):
    """
    To add cron job into the queue.

    :param  time:string    -- time string as format "%Y-%m-%d %H:%M:%S %w"
    :param  devEUI:int     -- devEUI of the device
    :param  command:string -- command compiled by command_handler
    """
    data = {}
    data["devEUI"] = devEUI
    data["command"] = command
    queue.hmset(time, data)
