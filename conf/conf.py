
import configparser
 
def createConfig(path):
    """
    Create a config file
    """
    config = configparser.ConfigParser()
    config.add_section("Settings")
    config.set("Settings", "ip", "192.168.15.43")
    config.set("Settings", "rtsp", "rtsp://192.168.11.33:554")
    config.set("Settings", "model_name", "ssd_mobilenet_v2_coco_2018_03_29")
    config.set("Settings", "port", "80")
    config.set("Settings", "login", "admin")
    config.set("Settings", "password", "Supervisor")
    config.set("Settings", "wsdl path", "/etc/onvif/wsdl/")
    
    with open(path, "w") as config_file:
        config.write(config_file)
 
 
if __name__ == "__main__":
    path = "settings.ini"
    createConfig(path)