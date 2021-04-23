import os

#os.chdir('..')
import sys
activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))
from onvif import ONVIFCamera
import configparser
pwd = os.getcwd()
print pwd

config = configparser.ConfigParser()
config.read(pwd + "/conf/settings.ini")
mycam_ip        = config.get("Settings","ip")
mycam_port      = config.get("Settings","port")
mycam_login     = config.get("Settings","login")
mycam_password  = config.get("Settings","password")
mycam_wsdl_path = config.get("Settings","wsdl_path")


try:
  mycam = ONVIFCamera('192.168.15.42', mycam_port, mycam_login, mycam_password, mycam_wsdl_path)
  print "[INFO]     Successful conection ONVIFCamera"
except:
  err_msg = "[ERROR]    Error with conect ONVIFCamera..."
  print err_msg
  print "[INFO]     Check the correctness of the entered data in the setings.ini (ip,port,login, password or wsdl_path)"
  send_msg(msg=err_msg)
  sys.exit(0)

# port
#print mycam.devicemgmt.GetNetworkProtocols()
#
ptz_service = mycam.create_ptz_service()
print mycam.devicemgmt.GetServices({'IncludeCapability': True})

# event
# to_dict
# events
# services
# devicemgmt
## ws_client
##
# ptz
# 



#print mycam
'''
resp = mycam.devicemgt.GetHostname()
#print resp



media = mycam.create_media_service()

profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
#print mycam.ptz

request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
print ptz_configuration_options
request = ptz.create_type('AbsoluteMove')
#print request
request.ProfileToken = profile._token

request.Position.PanTilt._x = 0.0114
request.Position.PanTilt._y = -0.0116
request.Speed.PanTilt._x = 1
request.Speed.PanTilt._y = 1
#print ptz.create_type('GetConfiguration')
ptz.AbsoluteMove(request)



request = ptz.create_type('ContinuousMove')
request.ProfileToken = profile._token

lenght = 1280.0
width = 720.0
centr_x = 114.0
centr_y = -116.0
mov_x = 1899.0
mov_y = 3937.0
x = 100
y = 100'''
'''
camera_x = ptz.GetStatus().Position.PanTilt._x
camera_y = ptz.GetStatus().Position.PanTilt._y
print (camera_x, " : ", camera_y)
camera_x = camera_x * 10000
camera_y = camera_y * 10000
print (camera_x, " : ", camera_y)

len_x = -(camera_x - centr_x - mov_x + (mov_x*2/lenght)*x)
len_y = camera_y - centr_y - mov_y + (mov_y*2/width)*y
print (len_x, " : ", len_y)

vec_x = len_x/(mov_x*2)
vec_y = len_y*3/(mov_y*2)
print (vec_x, " : ", vec_y)

vec_y = int(vec_y*100)/100.0
vec_x = int(vec_x*100)/100.0

print (str(vec_y), " : ", str(vec_x))
#print (ptz.GetStatus())
#while True:
#    print (ptz.GetStatus().Position.PanTilt._x,' : ',ptz.GetStatus().Position.PanTilt._y)

'''