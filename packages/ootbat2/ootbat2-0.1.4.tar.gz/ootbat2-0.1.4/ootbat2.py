#!/usr/bin/python

import os, re, time, subprocess, shutil, requests, tempfile, sys
from playsound import playsound

low_battery_setting = 10
path_sysfs_power_supply = '/sys/class/power_supply'
url_wav_file = 'https://tinyurl.com/2j7xcras'


def get_oot_low_health_wav() -> str:
    attempts = 5
    while attempts > 0:
        response = requests.models.Response()
        try:
            response = requests.get(url_wav_file)
        except Exception as e:
            pass
        if response.status_code == 200:
            break
        attempts -= 1
        time.sleep(1)
    else:
        print('Error, could not download wav file!')
        sys.exit(1)

    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
    temp_file.write(response.content)
    temp_file.close()
    return temp_file.name


def get_number_of_batteries() -> int:
    return len([f for f in os.listdir(path_sysfs_power_supply) if re.match(r'^BAT\d+$', f)])


def get_battery_data(number_of_batteries: int) -> dict:
    battery_data = dict()
    for n in range(number_of_batteries):
        battery_name = f'BAT{n}'
        path_battery = os.path.join(path_sysfs_power_supply, battery_name)
        path_battery_capacity = os.path.join(path_battery, 'capacity')
        path_battery_status = os.path.join(path_battery, 'status')
        with open(path_battery_capacity) as f:
            battery_percentage = int(f.read())
        with open(path_battery_status) as f:
            battery_status = f.read().strip()
        battery_data[battery_name] = {
            'percentage': battery_percentage,
            'status': battery_status
        }
    return battery_data


def main():
    number_of_batteries = get_number_of_batteries()
    notify_send_exists = shutil.which('notify-send') is not None

    wav_file_path = str()
    wav_local_path1 = './OOT_LowHealth.wav'
    wav_local_path2 = os.path.expanduser('~/media/OOT_LowHealth.wav')
    wav_check_local1 = os.path.exists(wav_local_path1)
    wav_check_local2 = os.path.exists(wav_local_path2)
    if wav_check_local1:
        wav_file_path = wav_local_path1
    elif wav_check_local2:
        wav_file_path = wav_local_path2
    else:
        wav_file_path = get_oot_low_health_wav()

    try:
        while True:
            battery_data = get_battery_data(number_of_batteries)
            battery_percentage = sum(battery['percentage'] for battery in battery_data.values())
            battery_statuses = {battery['status'] for battery in battery_data.values()}
            if (battery_percentage < low_battery_setting) and ('Discharging' in battery_statuses):
                if notify_send_exists:
                    subprocess.run(['notify-send', 'ootbat2', 'Low battery, charge me!'])
                playsound(wav_file_path)
            time.sleep(3)
    except KeyboardInterrupt:
        pass


if __name__ == '__main__':
    main()
