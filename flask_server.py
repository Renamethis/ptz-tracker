import os
import sys
from flask import Flask
from flask import request
from flask import jsonify
import configparser
import signal
import subprocess


pwd = os.getcwd()
orb_pid = None
sys.path.append(pwd+'/classes')
config_path = pwd + '/conf/settings.ini'
pid_path = pwd + '/log/pid'
python_bin = "venv/bin/python3.8"
tracking_file = "scripts/tracker.py"
autoset_file = "scripts/auto_set.py"
orb_path = 'ORB_SLAM2/orb_module/build/orb_module'
import Utility_Functions as UF


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
            if len(pid_lines) != 0 and check_pid(int(pid_lines[0])):
                return error('Tracking already running, stop this one before start new')
            tracking = subprocess.Popen([python_bin, tracking_file])
            pid = int(tracking.pid)
            with open(pid_path, 'w') as f:
                f.write(str(int(pid)))
            ''' ORB_SLAM2 IN DEVELOPING
            if(os.path.isfile(orb_path)):
                voc_path = 'ORB_SLAM2/Vocabulary/ORBvoc.txt'
                orb_path = './' + orb_path
                rtsp_url = UF.get_setting("rtsp")
                cam_cal = 'ORB_SLAM2/orb_module/Asus.yaml'
                orb_slam = subprocess.Popen([orb_path, voc_path, cam_cal, rtsp_url])
                orb_pid = orb_slam.pid
            '''
            print("Tracker successful started on pid: " + str(pid))
            return answer('Tracker started', {'pid': pid})
        elif data['command'] == 'stop':
            try:
                os.kill(int(pid_lines[0]), signal.SIGTERM)
                os.kill(orb_pid, signal.SIGTERM)
                with open(pid_path, 'w') as pid_file:
                    pid_file.write('')
            except:
                return error('Internal error. Try to restart server and check log to get more information')
            return answer('Tracker stopped')
        elif data['command'] == 'autoset':
            if len(pid_lines) != 0 and check_pid(int(pid_lines[0])):
                return error('Cant run autoset while tracking is processing')
            autoset = subprocess.Popen([python_bin, autoset_file])
            pid = int(autoset.pid)
            with open(pid_path, 'w') as f:
                f.write(str(int(pid)))
            print("Autoset successful started on pid: " + str(pid))
            return answer('Autoset started', {'pid': pid})
        elif data['command'] == 'create':
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
        'status': 'Error',
        'description': err
    }), 400


def answer(type, data=None):
    return jsonify({
        'status': type,
        'information': data
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
