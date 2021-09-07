from flask import Flask, request, jsonify
from json import dumps
from requests import post, get
api_key = 'c745cc1883a84f9bbe3252d865009a52'
erudite_url = 'https://nvr.miem.hse.ru/api/erudite/'
erudite_headers = {
    "accept": "application/json",
    "Content-Type": "application/json",
    "key": api_key
 }
app = Flask(__name__)


@app.route('/', methods=['GET', 'POST'])
def server():
    if request.method == 'POST':
        data = request.get_json(force=True)
        try:
            if(data['command'] == 'start' or data['command'] == 'stop' or data['command'] == 'autoset'): # Запуск/Остановка трекера
                # Запрос к базе данных erudite
                response = get(erudite_url + 'equipment?room_name='
                               + data['room_name'], headers=erudite_headers)
                if(response.content is None):
                    return error('Device is not exists', 10)
                device = response.json()[0]
                device_ip = device['ip']
                device_port = device['port']
                response = post('http://' + device_ip + ':' +
                                str(device_port) + '/track',
                                data=dumps({'command': data['command']}))
                print(response.json())
                if(response.json()['status'] != 'Error'):
                    return answer('Ok', 'Command ' + data['command']
                                  + ' Successfully executed')
                else:
                    return error(response.json()['description'], 3)
            elif(data['command'] == 'create'): # Создание нового устройства
                response = get(erudite_url + 'equipment?ip='
                               + data['device_ip'] + '&port=' +
                               data['device_port'], headers=erudite_headers)
                if(response.content is not None):
                    return error('This devie already exists', 11)
                response = get(erudite_url + 'rooms?ruz_number=' +
                               data['room_name'], headers=erudite_headers)
                if(response.json is None):
                    return error('Room is not exists', 12)
                camera_ip = data['camera_ip']
                camera_port = int(data['camera_port'])
                device_ip = data['device_ip']
                device_port = data['device_port']
                response = post(erudite_url + 'equipment',
                headers = erudite_headers, data=dumps({
                    'name': data['name'],
                    'type': data['type'],
                    'ip': device_ip,
                    'port': device_port,
                    'room_name': data['room_name']
                }))
                if(response.json()['message'] == 'Equipment added successfully'):
                    response = post("https://" + device_ip + ":" + device_port + "/track", data=dumps({
                        'command': 'create',
                        'port': camera_port,
                        'ip': camera_ip
                    }))
                    if(response.json()['status'] == 'Error'):
                        return error('Problem with device setting', 7)
                    else:
                        return error('Problems with equipment updating', 6)
                else:
                    return error('Invalid data', 4)
                return answer('Ok', 'Device successfully created')
            else:
                return error('Command doesnt exist', 0)
        except:
            return error('Data format is incorrect', 1)


def error(desc, code): # Функция для возврата ошибки
    return jsonify({
        'status': 'Error',
        'code': code,
        'description': desc
    }), 400


def answer(type, data=None): # Функция для возврата ответа от сервера
    return jsonify({
        'status': type,
        'information': data
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
