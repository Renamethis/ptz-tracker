activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

import sys
import os
#sys.path.append("./models/reserch")
#os.system('pwd')
#os.chdir('models/research')
#os.system('export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim')
#os.chdir('object_detection')

from onvif import ONVIFCamera
mycam = ONVIFCamera('192.168.11.52', 2000, 'admin', 'Supervisor', '/home/ilya/git/MM.Tracker/venv/wsdl')



media = mycam.create_media_service()
profile = media.GetProfiles()[0]
ptz = mycam.create_ptz_service()
request = ptz.create_type('GetConfigurationOptions')
request.ConfigurationToken = profile.PTZConfiguration._token
ptz_configuration_options = ptz.GetConfigurationOptions(request)
request = ptz.create_type('AbsoluteMove')
request.ProfileToken = profile._token
request.Position.PanTilt._x = 0.5
request.Position.PanTilt._y = 0.5

request.Speed.PanTilt._x = 1
request.Speed.PanTilt._y = 1

ptz.AbsoluteMove(request)


print request
