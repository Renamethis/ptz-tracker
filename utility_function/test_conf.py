import configparser
import os

cwd = os.getcwd()
print cwd

config = configparser.ConfigParser()
config.read("conf/settings.ini")

print config

value = config.get("Settings", "ip")
print value