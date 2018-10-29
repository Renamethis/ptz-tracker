import os
from onvif import ONVIFCamera
os.chdir('..')

#activate_this_file = "venv/bin/activate_this.py"
#execfile(activate_this_file, dict(__file__=activate_this_file))


mycam = ONVIFCamera('192.168.11.52', 2000, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl').create_media_service().GetProfiles()[0]
print mycam



media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('AbsoluteMove')
request.ProfileToken = profile._token

request.Position.PanTilt._x = 0.0114
request.Position.PanTilt._y = -0.0116
request.Speed.PanTilt._x = 1
request.Speed.PanTilt._y = 1

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
y = 100

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

