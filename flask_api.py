# activate_this_file = "venv/bin/activate_this.py"
# execfile(activate_this_file, dict(__file__=activate_this_file))

from flask import Flask, render_template, request
import cherrypy
from paste.translogger import TransLogger
import configparser

import json
import os


config_file = '/home/ubuntu/MM.Tracker/conf/settings.ini'

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
        print(data)
        ideal_data ={
            'ip': '0.0.0.0',
            'port': 43,
        }

        ip = data['ip'] if 'ip' in data else None

        port = data['port'] if 'port' in data else 80

        config = configparser.ConfigParser()
        config.read(config_file)
        config['Settings']['ip'] = str(ip)
        config['Settings']['port'] = str(port)

        with open(config_file, 'w') as configfile:
            config.write(configfile)

        # TODO Run script
        os.system('screen -S Tracking -dm bash -c "cd /home/ubuntu/MM.Tracker/; python test_scripts/test_classes.py;"')

        return 'Tracking: {}'.format(data)
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