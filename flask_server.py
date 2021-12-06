import os
import sys
from flask import Flask
from flask import request
from flask import jsonify
import configparser
from classes.Tracker import Tracker


pwd = os.getcwd()
orb_pid = None
sys.path.append(pwd+'/classes')
config_path = pwd + '/settings.ini'
orb_path = 'ORB_SLAM2/orb_module/build/orb_module'
sections = ['Onvif', 'Processing', 'AutoSet', 'Hardware']
tracker = Tracker()

app = Flask(__name__)


@app.route('/track', methods=['GET', 'POST'])
def tracker_listener():
    if request.method == 'POST':
        data = request.get_json(force=True)
        if data['command'] == 'start':
            if(not tracker.running):
                tracker.update_data()
                if(not tracker.start_tracker()):
                    return error('Error with tracker starting, '
                                 + 'check logs to get more information')
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
            return answer('OK', data={'information':
                                      'Tracker successfully started'})
        elif data['command'] == 'assistant':
            if(not tracker.running):
                tracker.update_data()
                if(not tracker.start_assistant()):
                    return error('Error with assistant starting, '
                                 + 'check logs to get more information')
        elif data['command'] == 'autoset':
            if(not tracker.running):
                tracker.update_data()
                if(not tracker.start_autoset()):
                    return error('Error with autoset starting, '
                                 + 'check logs to get more information')
            else:
                return error('Tracker already running')
            return answer('OK', data={'information':
                                      'Autoset sucessfully started'})
        elif data['command'] == 'stop':
            if(tracker.running):
                tracker.stop()
                return answer('OK', data={'information':
                                          'Tracker sucessfully stopped'})
            else:
                return error('Tracker is not running')
            return answer('Tracker stopped')
        elif data['command'] == 'track':
            if(tracker.running and tracker.is_assistant()):
                tracker.set_track(data["id"])
                return answer('OK', data={'information':
                                          'Track id set successfully'})
            else:
                return error('Assistant is not running')
        elif data['command'] == 'log':
            if(tracker.running):
                return answer('OK', data={'log': tracker.get_status_log()})
            else:
                return error('Tracker is not running')
        elif data['command'] == 'set':
            if(tracker.running):
                return error('You cant change parameters'
                             + 'while tracker is running')
            Config = configparser.ConfigParser()
            Config.read(config_path)
            keys = list(data.keys())
            keys.remove('command')
            flag = False
            for key in keys:
                for sec in sections:
                    items = [item[0] for item in Config.items(sec)]
                    if(key in items):
                        Config.set(sec, key, data[key])
                        flag = True
                        break
                if(not flag):
                    return error('Invalid parameter(s)')
                flag = True
            cfile = open(config_path, 'w')
            Config.write(cfile)
            cfile.close()
            tracker.update_data()
            return answer('OK', data={'information':
                                      'Data successfully set up'})
        elif data['command'] == 'status':
            status = str(tracker.status).split('.')[1]
            return answer('OK', data={'status': status})
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
