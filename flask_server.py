import os
import sys
#activate_this_file = "venv/bin/activate_this.py"
#exec(compile(open(activate_this_file, "rb").read(), activate_this_file, 'exec'), dict(__file__=activate_this_file))
pwd = os.getcwd()
sys.path.append(pwd+'/classes')
config_path = pwd + '/conf/settings.ini'
pid_path = pwd + '/log/pid'
python_bin = "venv/bin/python"
script_file = "scripts/tracker.py"
from flask import Flask
from flask import request
from flask import jsonify
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
		data = request.get_json(force=True)
		if data['command'] == 'start':
			if len(pid_lines) != 0 and check_pid(int(pid_lines[0])) :
				return error('Tracking already running, stop this one before start new')
			tracking = subprocess.Popen([python_bin, script_file])
			time.sleep(0.2)
			pid = int(tracking.pid)
			with open(pid_path, 'w') as f:
				f.write(str(int(pid)))
			print("Tracker Successful started on pid: " + str(pid))
			return answer('Tracker started', {'pid':pid})
		elif data['command'] == 'stop':
			try:
				os.kill(int(pid_lines[0]), signal.SIGTERM)
				with open(pid_path, 'w') as pid_file:
					pid_file.write('')
			except:
				return error('Internal error. Try to restart server and check log to get more information')
			return answer('Tracker stopped')
		elif data['command'] == 'set':
			port = data['port']
			ip = data['ip']
			rtsp = "rtsp://" + ip + ':554'
			config = configparser.ConfigParser()
			config.read(config_path)
			config.set('Settings', 'ip', ip)
			config.set('Settings', 'rtsp', rtsp)
			config.set('Settings', 'port', port)
			config.set('Settings', 'login', 'admin')
			config.set('Settings', 'password', 'Supervisor')
			with open(config_path, "w") as config_file:
				config.write(config_file)
			return answer('Data set up successfully')
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
	}), 200
if __name__ == '__main__':
	app.run(host='0.0.0.0', port='5000')
