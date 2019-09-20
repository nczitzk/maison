from config import configs

import json
import time


def judge(device, number):
    """
    To judge whether the querying device exists
    by searching in ids and devices.

    :param  device:string -- device name (eg. light, fan...)
    :param  number:int    -- device number (eg. 0 for all, 1 for No.1...)
    :return bool
    """
    if device in configs["id"] and device in configs["devices"]:
        if str(number) in configs["devices"][device] or number is 0:
            return True
    else:
        return False


def get_timestamp(when, unit="ms"):
    """
    To calculate time into timestamp in "s" or "ms".
    "ms" by default.

    :param  when:string -- time string as format "%Y-%m-%d %H:%M:%S %w"
    :param  unit:string -- "s" or "ms"
    :return timestamp
    """
    if when == "now":
        return int(time.time()) if unit == "s" else int(round(time.time() * 1000))
    else:
        time_float = time.mktime(time.strptime(when, "%Y-%m-%d %H:%M:%S %w"))
        return int(time_float) if unit == "s" else int(round(time_float) * 1000)
