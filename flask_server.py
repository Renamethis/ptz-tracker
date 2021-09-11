import os
import sys
from flask import Flask
from flask import request
from flask import jsonify
import configparser
# import classes.Utility_Functions as UF
from scripts.tracker import Tracker


pwd = os.getcwd()
orb_pid = None
sys.path.append(pwd+'/classes')
config_path = pwd + '/conf/settings.ini'
python_bin = "venv/bin/python3.8"
tracking_file = "scripts/tracker.py"
autoset_file = "scripts/auto_set.py"
orb_path = 'ORB_SLAM2/orb_module/build/orb_module'
tracker = Tracker()

app = Flask(__name__)


@app.route('/track', methods=['GET', 'POST'])
def tracker_listener():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['command'] == 'start':
            if(not tracker.running):
                if(not tracker.start_tracker()):
                    return error('Error with tracker staring,' +
                                 'check logs to get more information')
            else:
                return error('Tracker already running')
            ''' ORB_SLAM2 IN DEVELOPING
            if(os.path.isfile(orb_path)):
                voc_path = 'ORB_SLAM2/Vocabulary/ORBvoc.txt'
                orb_path = './' + orb_path
                rtsp_url = UF.get_setting("rtsp")
                cam_cal = 'ORB_SLAM2/orb_module/Asus.yaml'
                orb_slam = subprocess.Popen([orb_path, voc_path, cam_cal, rtsp_url])
                orb_pid = orb_slam.pid
            '''
            return answer('Tracker successfully started')
        elif data['command'] == 'stop':
            if(tracker.running):
                tracker.stop()
            else:
                return error('Tracker not launched')
            return answer('Tracker stopped')
        elif data['command'] == 'autoset':
            if(not tracker.running):
                if(not tracker.start_autoset()):
                    return error('Error with autoset staring,' +
                                 'check logs to get more information')
            else:
                return error('Tracker already running')
            return answer('Autoset sucessfully started')
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
        elif data['command'] == 'status':
            status = str(tracker.status).split('.')[1]
            return answer("Status of tracking", data={'status': status})
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
