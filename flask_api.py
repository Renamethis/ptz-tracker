from flask import Flask, render_template, request
import cherrypy
from paste.translogger import TransLogger

import json

app = Flask(__name__)

@app.route('/')
def homepage():
    return """<h1>Face recognition and tracking API</h1><br><br>
    Results URL: {}<br>
    On/off endpoint: {}<br>
    Documentation: {}<br>
    """


@app.route('/tracking', methods=['GET', 'POST'])
def tracking_url():
    if request.method == 'POST':
        data = json.loads(request.data)
        print(data)
        return 'Tracking: {}'.format(request.data)
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