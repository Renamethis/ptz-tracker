activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

from onvif import ONVIFCamera

mycam = ONVIFCamera('192.168.1.60', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
media_profile = media.GetProfiles()[0];
token = media_profile._token
GS = ptz.create_type('GetStatus') 
GS.ProfileToken = token 
print ptz.GetStatus(GS)[0][1]._x