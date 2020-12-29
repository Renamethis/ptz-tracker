# PTZ Tracker
ПО, предназначенное для наведения onvif-камеры на человека

**Требования для запуска**


- Nvidia Jetson Nano/CPU Server(Размещение трекера)
- Control CPU Server(Можно разместить там же, где и трекер)
- Onvif-камеры

**Установка**


1. Загрузите репозиторий

`git clone git.miem.hse.ru/592/ptz-tracker.git
`

2. Перейдите в папку трекера

`cd ptz-tracker
`

3. Запустите установочный файл

`./setup
`

**Запуск**


- Control Server:

`. ./venv/bin/activate
python3 control_server.py
`

- Tracker Server:

`. ./venv/bin/activate
python3 flask_server.py
`