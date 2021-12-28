# PTZ Tracker
ПО, предназначенное для наведения onvif-камеры на человека

**Требования для запуска**


- Nvidia Jetson Nano/CPU Server(Размещение трекера)
- Control CPU Server(Можно разместить там же, где и трекер)
- Onvif-камеры

**Установка**


1. Загрузите репозиторий

`git clone git.miem.hse.ru/592/ptz-tracker.git`

2. Перейдите в папку трекера

`cd ptz-tracker`

3. Перейдите в директорию установочных файлов

`cd setup_files`

4. Запустите установочный файл

- CPU:

`. ./setup.sh `

- Jetson:

`. ./setup.sh {JetPack version}`

5. Запустите установочный файл GStreamer в директории setup_files

`. ./gstreamer_install.sh`

6. Запустите установочный файл OpenCV в директории setup_files

`. ./build_opencv.sh`

> В процессе установки система может запросить подтверждение пароля или пакетный менеджер может запросить подтверждение установки пакетов.

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
