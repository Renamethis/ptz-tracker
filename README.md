# PTZ Tracker - версия с модулем multiprocessing
ПО, предназначенное для наведения onvif-камеры на человека

**Требования для запуска**


- Nvidia Jetson Nano/CPU Server(Размещение трекера)
- Control CPU Server(Можно разместить там же, где и трекер)
- Onvif-камеры

**Установка**


1. Загрузите репозиторий

`git clone git.miem.hse.ru/592/ptz-tracker.git -b multiprocessing`

2. Перейдите в папку трекера

`cd ptz-tracker`

3. Перейдите в директорию установочных файлов

`cd setup_files`

4. Запустите установочный файл

- CPU:

`. ./setup.sh `

- Jetson:

`. ./setup.sh {JetPack version}`

**Запуск**

Активируйте виртуальное окружение:

`. ./venv/bin/activate`

Запустите сервер:

`python3 flask_server.py`

**Установка сервиса**

Для работы сервера трекера в фоновом режиме необходимо установить сервис трекера, предварительно изменив поля WorkingDirectory, ExecStart с правильными путями в файле tracker.service

`sudo mv tracker.service /etc/systemd/system/tracker.service`

`sudo systemctl enable tracker`

`sudo systemctl restart tracker`
