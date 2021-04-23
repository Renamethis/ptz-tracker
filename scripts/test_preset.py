
activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))

from onvif import ONVIFCamera



mycam = ONVIFCamera('192.168.1.60', 80, 'admin', 'Supervisor', '/etc/onvif/wsdl/')
media = mycam.create_media_service()
ptz = mycam.create_ptz_service()
#ptz.GetNodes()[0]['HomeSupported'] is True

profile = media.GetProfiles()[0]
request = {k: ptz.create_type(k) for k in ['ContinuousMove', 'GotoHomePosition', 'AbsoluteMove', 'RelativeMove', 'SetHomePosition']}

for _, r in request.items(): r.ProfileToken = profile._token


ptz.SetHomePosition(request['SetHomePosition'])
ptz.GotoHomePosition(request['GotoHomePosition'])