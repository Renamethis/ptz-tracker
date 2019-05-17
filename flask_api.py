activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

from flask import Flask, render_template, request
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

app = Flask(__name__)

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

                config = configparser.ConfigParser()
                config.read(config_file)
                config['Settings']['ip'] = str(ip)
                config['Settings']['port'] = str(port)

                with open(config_file, 'w') as configfile:
                    config.write(configfile)

                # Run Tracking Script
                tracking_proc = subprocess.Popen('screen -S Tracking -dm bash -c "cd /home/ibakhtizin/ololo/MM.Tracker/; python test_scripts/test_classes.py;"', shell=True)
                time.sleep(0.5)
                tracking_pid = tracking_proc.pid
                print("TRACKING PID:", int(tracking_pid)+2)

                # Save tracking PID to file
                with open(pid_file, 'a+') as f:
                    f.write(str(int(tracking_pid)+2))

                # TODO Run Recognition Script


                """
                screen -S Tracking -dm bash -c "cd /home/ibakhtizin/ololo/MM.Tracker/; python test_scripts/test_classes.py;"
                screen -S Recognition -dm bash -c "python3 recognition_subprocess.py;";
                screen -S WebAPI -dm bash -c "cd /home/ibakhtizin/miem_visi0n/Tracking_System; python3 main_flask.py;"
                screen -ls
                """


                # os.system('screen -S Tracking -dm bash -c "cd /home/ubuntu/MM.Tracker/; python test_scripts/test_classes.py;"')
                # proc2 =

                return 'Tracking started\nTracking PID: {}'.format(data, int(tracking_pid)+2)
            else:
                return 'Tracking already started with PID {}'.format(pid_list)

        elif data['command'] == 'stop':

            for pid in pid_list:
                os.kill(int(pid), signal.SIGTERM)

            with open(pid_file, 'w') as p_file:
                p_file.write('')

            return 'Tracking STOPED and pid file clean'

    else:
        return 'Tracking on/off method'





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