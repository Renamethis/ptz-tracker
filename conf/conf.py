
import configparser
import os
def createConfig(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    ip = raw_input("Enter IP adress: ")
    rtsp = raw_input("Enter address of rtsp-thread: ")
    login = raw_input("Enter login: ")
    password = raw_input("Enter password: ")
    config.set("Settings", "ip", ip)
    config.set("Settings", "rtsp", rtsp)
    config.set("Settings", "model_name", "ssd_mobilenet_v2_coco_2018_03_29")
    config.set("Settings", "port", "80")
    config.set("Settings", "login", login)
    config.set("Settings", "password", password)
    config.set("Settings", "wsdl_path", os.path.abspath(os.getcwd()).split('ptz-tracker')[0] + 'ptz-tracker/wsdl')
    with open(path, "w") as config_file:
        config.write(config_file)
 
 
if __name__ == "__main__":
    path = "settings.ini"
    createConfig(path)
