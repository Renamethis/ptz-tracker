from flask import Flask, request
from json import dumps
from requests import post, get
from enum import Enum, auto


class ServerError(Enum):
    InvalidCommand = auto()
    NoCommandProvided = auto()
    DeviceNotFound = auto()
    TrackerError = auto()


COMMANDS = ['start', 'autoset', 'stop', 'set', 'status']
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
            if(data['command'] in COMMANDS):
                # Запрос к базе данных erudite
                response = get(erudite_url + 'equipment?room_name='
                               + data['room_name'], headers=erudite_headers)
                if(response.content is None):
                    return error('The tracker is not set on provided room',
                                 ServerError.DeviceNotFound)
                device = response.json()[0]
                device_ip = device['ip']
                device_port = device['port']
                # Передаем все параметры для команды set(если они есть)
                body = {}
                for key in data.keys():
                    if(key != 'room_name'):
                        body[key] = data[key]
                # Отправляем запрос на необходимое устройство
                response = post('http://' + device_ip + ':' +
                                str(device_port) + '/track',
                                data=dumps(body))
                if(response.json()['status'] != 'Error'):
                    return answer('Ok', 'Command ' + data['command']
                                  + ' Successfully executed')
                else:
                    return error(response.json()['description'],
                                 ServerError.TrackerError)
            else:
                return error('Command doesnt exist',
                             ServerError.InvalidCommand)
        except KeyError:
            return error('Data format is incorrect',
                         ServerError.NoCommandProvided)


# Функция для возврата ошибки
def error(desc, code):
    return dumps({
        'status': 'Error',
        'code': code,
        'description': desc
    }), 400


# Функция для возврата ответа от сервера
def answer(type, data=None):
    return dumps({
        'status': type,
        'information': data
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0')
