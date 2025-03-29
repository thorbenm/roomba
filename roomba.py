from time import time, sleep
import datetime
import subprocess
import os
from login_data import IRBT_LOGIN, IRBT_PASSWORD
import json


def login():
    os.environ['IRBT_LOGIN'] = IRBT_LOGIN
    os.environ['IRBT_PASSWORD'] = IRBT_PASSWORD


login()


def force_start():
    subprocess.run("irbt-cli.py -c start".split(), capture_output=True, text=True)


def stop():
    subprocess.run("irbt-cli.py -c stop".split(), capture_output=True, text=True)
    sleep(5.0)
    subprocess.run("irbt-cli.py -c dock".split(), capture_output=True, text=True)


def enabled():
    with open("/home/pi/Programming/roomba/disabled_until", "r") as f:
        disabled_until = int(f.read())
        return disabled_until < int(time())


def start():
    if 7 <= datetime.datetime.now().hour < 20:
        if enabled():
            t = datetime.datetime.now() - datetime.timedelta(hours=18)
            if get_cleaning_time_since(t) <= 20:
                force_start()


def clean_room(room):
    output = subprocess.check_output('irbt-cli.py -l', shell=True, text=True)

    room_map = {}
    for line in output.splitlines():
        name, id_str = line.split(': ')
        name = name.lower().replace("'", "")
        room_map[name] = int(id_str)

    room_id = room_map[room.lower()]
    subprocess.run(f"irbt-cli.py -r {room_id} -c start".split(), capture_output=True, text=True)


def start_if_really_needs_to():
    if enabled():
        t = datetime.datetime.now() - datetime.timedelta(hours=72)
        if get_cleaning_time_since(t) <= 5:
            force_start()


def get_cleaning_time_since(since):
    # in minutes
    output = subprocess.check_output('irbt-cli.py -M', shell=True, text=True)
    data = json.loads(output)
    timestamp_threshold = since.timestamp()
    total_minutes = sum(item['durationM'] for item in data if timestamp_threshold <= item['timestamp'] )
    return total_minutes


def disable_for(time_string):
    unit = time_string[-1]
    value = time_string[:-1]
    if unit == "s":
        t = int(value)
    if unit == "m":
        t = int(value) * 60
    if unit == "h":
        t = int(value) * 60 * 60
    if unit == "d":
        t = int(value) * 60 * 60 * 24
    with open("/home/pi/Programming/roomba/disabled_until", "w") as f:
        f.write(str(int(time()) + t))
