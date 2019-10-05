from config import configs
from mqtt import init, run_cron
from handlers import state_handler, command_handler

import os
import threading
from sanic import Sanic
from sanic.response import json, text

app = Sanic(__name__)
path = os.path.dirname(os.path.abspath(__file__))


@app.route("/", methods=['GET', 'POST'])
async def main(request):
    return text("Please GET /states or /command to fetch API docs")


@app.get("/state/")
async def state_doc(request):
    """To fetch /state API doc."""
    with open(os.path.join(path, "doc", "state"), 'r') as f:
        return text(f.read())


@app.post("/state/<device:string>/<number:int>/")
async def state(request, device, number):
    """To fetch state of certain device."""
    return text(state_handler(device, number, request.json))


@app.get("/command/")
async def command_doc(request):
    """To fetch /command API doc."""
    with open(os.path.join(path, "doc", "command"), 'r') as f:
        return text(f.read())


@app.post("/command/<device:string>/<number:int>/")
async def command(request, device, number):
    """To issue commands to certain device and get results."""
    return text(command_handler(device, number, request.json))

if __name__ == "__main__":
    crons = []

    # "tx" refers to downlink topics
    # "rx" refers to uplink topics
    command_thread = threading.Thread(target=init("tx"))
    state_thread = threading.Thread(target=init("rx"))
    command_thread.start()
    state_thread.start()
    run_cron(3)
    app.run(host=configs["app_host"], port=configs["app_port"])
