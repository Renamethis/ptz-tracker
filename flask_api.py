activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

from flask import Flask, render_template, request
from wsdiscovery import WSDiscovery
import cherrypy
from paste.translogger import TransLogger
import configparser
import subprocess

import time

import json
import os
import signal


config_file = '/home/ubuntu/MM.Tracker/conf/settings.ini'
pid_file ='/home/ubuntu/MM.Tracker/log/pid'
recognition_result_file = '/home/ibakhtizin/ololo/MM.Tracker/result.json'

app = Flask(__name__)


def discover():
    # discovery method
    try:
        cameras = []
        wsd = WSDiscovery()
        wsd.start()
        ret = wsd.searchServices()
        print('Discovered {} services:'.format(len(ret)))
        for i, service in enumerate(ret):
            if 'onvif' in service.getXAddrs()[0]:
                ip, port = get_ip_and_port_from_str(service.getXAddrs()[0])
                cameras.append({'ip': ip, 'port': port})
        wsd.stop()
        return cameras

    except Exception as e:
        print(e)
        print('Failed to discover services')
        return

def get_ip_and_port_from_str(ip_str):
    ip = ip_str.split('.')
    ip = ip[len(ip) - 1].split(':')
    ip = ip[0].split('/')[0]

    port = ip_str
    if port.count(':') > 1:
        port = port.split('.')
        port = port[len(port) - 1].split(':')
        port = port[len(port) - 1].split('/')
        port = port[0]
    else:
        port = 80
    network = ip_str
    network = network.split('/')
    network = network[2].split('.')
    network = network[0] + '.' + network[1] + '.' + network[2]

    ip = str(network) + '.' + str(ip)
    # print('IP: {}, Port: {}'.format(ip, port))
    return ip, port


@app.route('/')
def homepage():
    return """<h1>Face recognition and tracking API</h1><br>
    Results URL: {}<br>
    On/off endpoint: {}<br>
    Documentation: {}<br>
    """


@app.route('/tracking', methods=['GET', 'POST'])
def tracking_url():
    if request.method == 'POST':
        data = request.get_json()
        ideal_data = {
            'command': 'start',
            'ip': '0.0.0.0',
            'port': 43,
        }

        with open(pid_file) as f:
            pid_list = f.readlines()

        print('PID LIST ({}): {}'.format(len(pid_list), pid_list))

        if data['command'] == 'start':
            if len(pid_list) < 1:
                ip = data['ip'] if 'ip' in data else None
                port = data['port'] if 'port' in data else 80
                login = data['login'] if 'login' in data else 'login'
                password = data['password'] if 'password' in data else 'password'

                config = configparser.ConfigParser()
                config.read(config_file)
                config['Settings']['ip'] = str(ip)
                config['Settings']['port'] = str(port)
                # TODO Save login and password from POST data to CONFIG

                with open(config_file, 'w') as configfile:
                    config.write(configfile)

                # Run Tracking Script
                tracking_proc = subprocess.Popen('screen -S Tracking -dm bash -c "cd /home/ibakhtizin/ololo/MM.Tracker/; python test_scripts/test_classes.py;"', shell=True)
                time.sleep(0.1)
                tracking_pid = tracking_proc.pid
                print("TRACKING PID:", int(tracking_pid)+2)

                # Save tracking PID to file
                with open(pid_file, 'a+') as f:
                    f.write(str(int(tracking_pid)+2))

                # # TODO Run Recognition Script
                # recognition_proc = subprocess.Popen('screen -S Recognition -dm bash -c "python3 recognition_subprocess.py;";', shell=True)
                # time.sleep(0.1)
                # recognition_pid = recognition_proc.pid
                # print("RECOGNITION PID:", int(recognition_pid) + 2)
                #
                # # Save recognition PID to file
                # with open(pid_file, 'a+') as f:
                #     f.write(str(int(recognition_pid) + 2))


                """
                screen -S Tracking -dm bash -c "cd /home/ibakhtizin/ololo/MM.Tracker/; python test_scripts/test_classes.py;"
                screen -S Recognition -dm bash -c "python3 recognition_subprocess.py;";
                screen -S WebAPI -dm bash -c "cd /home/ibakhtizin/miem_visi0n/Tracking_System; python3 main_flask.py;"
                screen -ls
                """


                # os.system'screen -S Tracking -dm bash -c "cd /home/ubuntu/MM.Tracker/; python test_scripts/test_classes.py;"')
                # proc2 =
                # {recognition_pid}

                return 'Tracking started' \
                       '' \
                       'Tracking PID: {tracking_pid}' \
                       'Recognition PID: ' \
                       'Input: {data}'.format(
                    tracking_pid=int(tracking_pid)+2,
                    # recognition_pid=int(recognition_pid) + 2,
                    data=data
                )
            else:
                out = 'Tracking already started with PID {}'.format(pid_list)
                print(out)
                return out

        elif data['command'] == 'stop':
            print("Stopping processes:", pid_list)
            for pid in pid_list:
                os.kill(int(pid), signal.SIGTERM)

            with open(pid_file, 'w') as p_file:
                p_file.write('')

            return 'Tracking STOPED and pid file clean'

    else:
        return 'Tracking on/off method'


@app.route('/recognition_result')
def recognition_result_json():
    with open(recognition_result_file, 'r') as file:
        data = file.read()
    return data


@app.route('/discovery')
def discovery():
    cameras = discover()
    return json.dumps(cameras)



def run_server():
    # Enable WSGI access logging via Paste
    app_logged = TransLogger(app)

    # Mount the WSGI callable object (app) on the root directory
    cherrypy.tree.graft(app_logged, '/')

    # Set the configuration of the web server
    cherrypy.config.update({
        'engine.autoreload_on': True,
        'log.screen': True,
        'server.socket_port': 5000,
        'server.socket_host': '0.0.0.0'
    })

    # Start the CherryPy WSGI web server
    cherrypy.engine.start()
    cherrypy.engine.block()


if __name__ == "__main__":
    run_server()