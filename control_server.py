from flask import Flask, request, jsonify
from json import dumps, loads
from requests import post, get
api_key = 'c745cc1883a84f9bbe3252d865009a52'
erudite_url = 'https://nvr.miem.hse.ru/api/erudite/'
erudite_headers = {
"accept" : "application/json",
 "Content-Type" : "application/json",
 "key": api_key
 }
app = Flask(__name__)
@app.route('/', methods=['GET', 'POST'])
def server():
    if request.method == 'POST':
        data = request.get_json(force=True)
        #try:
        if(data['command'] == 'start' or data['command'] == 'stop'): # Запуск/Остановка трекера
            # Запрос к базе данных erudite
            response = get(erudite_url + 'equipment', headers = erudite_headers)
            equipment = response.json()
            device_ip = '127.0.0.1'
            device_port = '5000'
            for device in equipment: # Поиск необходимого устройства
                if((device['type'] == 'Jetson' or device['type'] == 'Server')
                and device['room_name'] == data['room_name'] ):
                    device_ip = device['ip']
                    device_port = device['port']
                    break
            print(device_ip)
            response = post('http://' + device_ip + ':' + str(device_port) + '/track',
            data=dumps({'command':data['command']}))
            print(response.json())
            if(response.json()['status'] != 'Error'):
                return answer('Ok', 'Command ' + data['command']
                + ' Successfully executed')
            else:
                return error(response.json()['description'], 3)
        elif(data['command'] == 'create'): # Создание нового устройства
            response = get(erudite_url + 'equipment', headers = erudite_headers)
            equipment = response.json()['data']
            response = get(erudite_url + 'rooms', headers = erudite_headers)
            rooms = response.json()['data']
            camera_ip = data['camera_ip']
            device_ip = data['device_ip']
            device_port = data['device_port']
            if(not if_val(equipment, 'ip', device_ip) and if_val(rooms, 'ruz_number', data['room_name'])):
                response = post(erudite_url + 'equipment',
                headers = erudite_headers, data=dumps({
                'name' : data['name'],
                'type' : data['type'],
                'ip' : device_ip,
                'port' : device_port,
                'room_name' : data['room_name']
                }))
                if(response.json()['message'] == 'Equipment added successfully'):
                    response = post("https://" + device_ip + ":" + device_port + "/track", data=dumps({
                    'command':'set',
                    'port':80,
                    'ip':camera_ip
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
        #except:
        #    return error('Data format is incorrect', 1)
def error(desc, code): # Функция для возврата ошибки
	return jsonify({
		'status':'Error',
        'code': code,
		'description': desc
	}), 400
def answer(type, data=None): # Функция для возврата ответа от сервера
    return jsonify({
    	'status':type,
    	'information':data
	}), 400
def if_val(col, key, val):
    for record in col:
        try:
            if(record[key] == val):
                return True
        except:
            pass
    return False

if __name__ == '__main__':
    app.run(debug=True, port=152)
