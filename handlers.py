from config import configs
from utils import judge, get_timestamp
from cache import query_database, add_cron

import time
import json
from mqtt import issue_command

keys = json.loads(configs["device"]["_keys"])


def state_handler(device, number, form):
    """
    To fetch states of certain device with Structive Query Language SUPPORTED!

    :param  device:string -- device name (eg. light, fan...)
    :param  number:int    -- device number (eg. 1 for No.1...)
    :param  form  :json   -- argument form (see readme/state)
    :return json
    """
    if not judge(device, number):
        return "\"{}_{}\" does not exist".format(device, number)

    # To deconstruct <ResultSet> wrapper around database query result.
    info = []
    for resultset in query_database(device, number, form):
        info_generator = resultset.get_points()
        while True:
            try:
                info.append(next(info_generator))
            except StopIteration:
                break

    return json.dumps(info if len(info) > 1 else info[0])


def command_handler(device, number, form):
    """
    To tranlate raw command to command code (see readme/commands_code)
    and filter out invalid command.

    :param  device:string -- device name (eg. light, fan...)
    :param  number:int    -- device number (eg. 0 for all, 1 for No.1...)
    :param  form  :json   -- command form (see readme/commands)
    :return string
    """
    if not judge(device, number):
        return "\"{}_{}\" does not exist".format(device, number)

    # queue for sending commands through MQTT
    queue = {}
    # result list composed by successfully interpreted commands
    results = []
    # error list containing commands with invalid keys or values
    errors = []
    # If commands contain "_time", then make it a cron job
    cron = False
    timer = ""

    for (key, value) in form.items():
        if key in keys[device]:
            if value not in keys[device][key]:
                errors.append("value \"{}\" is not included in key \"{}\" of \"{}\" devices:\n".format(
                    value, key, device) + ", ".join(keys[device][key]))
                continue

            # "state" is ignored (see readme/command_code or readme/state_code)
            # Some values need to be translated into number form.
            states_str = "" if key == "state" else key + "_"
            value_str = configs["value"][str(value)] if str(
                value) in configs["value"] else str(value)

            # If commands acting on all devices of same type,
            # then push them into queue.
            if number == 0:
                for device_num in configs["devices"][device]:
                    queue["#{}_{}_{}{}".format(
                        configs["id"][device], device_num, states_str, value_str)] = device_num
                    results.append("{}_{}::{} -> {}".format(
                        device, device_num, key, value_str))
            else:
                queue["#{}_{}_{}{}".format(
                    configs["id"][device], number, states_str, value_str)] = str(number)
                results.append("{}_{}::{} -> {}".format(
                    device, number, key, value_str))
        elif key == "_timer":
            timer = value
            cron = True
        else:
            errors.append(
                "\"{}\" devices have no key \"{}\"".format(device, key))

    # Let us free the queue :D
    if cron:
        for (command, device_num) in queue.items():
            add_cron(
                timer, configs["devEUI"]["{}_{}".format(device, device_num)], command)
    else:
        for (command, device_num) in queue.items():
            issue_command(
                configs["devEUI"]["{}_{}".format(device, device_num)], command)

    # To generate the output for results
    output = (("the following commands {} issued{}:\n> {}".format(
        "will be" if cron else "have been",
        " at {}".format(timer) if cron else "",
        "\n> ".join(results))) if results else "") + \
        ((("\n" if results else "") +
          "errors have occured when parsing commands below:\n> {}".format(
            "\n> ".join(errors))) if errors else "")
    return output
