import os
import sys
activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))
pwd = os.getcwd()
sys.path.append(pwd+'/classes')
config_path = pwd + '/conf/settings.ini'
pid_path = pwd + '/log/pid'
from flask import Flask


from flask import request
from flask import jsonify
from OnvifInteraction import Camera
import configparser
import signal
import subprocess
import time

def check_pid(id):
	try:
		os.kill(id, 0)
	except OSError:
		return False
	else:
		return True
app = Flask(__name__)
@app.route('/track', methods=['GET', 'POST'])
def tracker_listener():
	if request.method == 'POST':
		with open(pid_path) as pid_file:
			pid_lines = pid_file.readlines()
		data = request.form
		if data['command'] == 'start':
			if len(pid_lines) <> 0 and check_pid(int(pid_lines[0])) :
				return error('Tracking already running, stop this one before start new')
			ip = data['ip']
			port = data['port']
			login = data['login']
			password = data['password']
			wsdl_path = pwd + '/wsdl'
			cam = Camera(ip, port, login, password, wsdl_path)
			if not cam.connect():
				return error('Data is invalid')
			rtsp = cam.getStreamUri()
			config = configparser.ConfigParser()
			config.read(config_path)
			config.set('Settings', 'ip', ip)
			config.set('Settings', 'rtsp', rtsp)
			config.set('Settings', 'port', port)
			config.set('Settings', 'password', password)
			config.set('Settings', 'wsdl_path', wsdl_path)
			with open(config_path, "w") as config_file:
				config.write(config_file)
			tracking = subprocess.Popen(['python2.7 ' +  pwd + '/test_scripts/test_classes.py'], shell=True)
			time.sleep(0.1)
			pid = int(tracking.pid) + 1
			with open(pid_path, 'w') as f:
				f.write(str(int(pid)))
			print "Tracker Successful started on pid: " + str(pid)
			return answer('Tracker started:', {'pid':pid, 'stream':rtsp})
		elif data['command'] == 'stop':
			try:
				os.kill(int(pid_lines[0]), signal.SIGTERM)
				with open(pid_path, 'w') as pid_file:
					pid_file.write('')
			except:
				return error('Internal error. Try to restart server and check log to get more information')
			return answer('Tracker stopped')
		else:
			return error('Bad command')
	else:
		return error('Only POST requests')
def error(err):
	return jsonify({
		'status':'Error',
		'description': err
	}), 400
def answer(type, data=None):
	return jsonify({
		'status':type,
		'information':data
	}), 400
if __name__ == '__main__':
	app.run()
