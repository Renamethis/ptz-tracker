from subprocess import Popen, PIPE
import sys
import os

out, err = Popen('ls | grep venv', shell=True, stdout=PIPE).communicate()
#print out
if out == 'venv\n':
    print ('Venv error...')
    sys.exit()


Popen('virtualenv --system-site-packages -p python2.7 ./venv', shell=True, stdout=PIPE).communicate()
print ('Venv done')



#os.system('source ./venv/bin/activate')
activate_this_file = "venv/bin/activate_this.py"
execfile(activate_this_file, dict(__file__=activate_this_file))
#os.system('/bin/bash  --rcfile venv/bin/activate')

'''
out, err = Popen('pip list | grep tensorflow-', shell=True, stdout=PIPE).communicate()
print ('-in venv-')
print out
print ('--')
'''

#foo = Popen('pip install --upgrade pip', shell=True, stdout=PIPE)
os.system('pip install --upgrade pip')
print ('pip upgrade done')

#foo = Popen('pip install tensorflow==1.5', shell=True, stdout=PIPE)
os.system('pip install tensorflow==1.5')
print ('tensorflow install done')

os.system('sudo apt-get install protobuf-compiler python-pil python-lxml python-tk')
print ('apt-get install done')
os.system('pip install --user Cython')
print ('Cython install done')
os.system('pip install --user contextlib2')
print ('contextlib2 install done')
os.system('pip install --user jupyter')
print ('jupyter install done')
os.system('pip install --user matplotlib')
print ('matplotlib install done')

os.system('git clone https://github.com/cocodataset/cocoapi.git')
os.system('git clone https://github.com/tensorflow/models.git')
os.chdir('cocoapi/PythonAPI')
os.system('pwd')
os.system('make')
os.chdir('..')
os.system('pwd')
os.chdir('..')
os.system('pwd')
os.chdir('models/research')
os.system('wget -O protobuf.zip https://github.com/google/protobuf/releases/download/v3.0.0/protoc-3.0.0-linux-x86_64.zip')
os.system('unzip protobuf.zip')
os.system('./bin/protoc object_detection/protos/*.proto --python_out=.')
os.system('export PYTHONPATH=$PYTHONPATH:`pwd`:`pwd`/slim')
os.chdir('..')
os.system('pwd')
os.chdir('..')
os.system('pwd')
os.system('cp -f utility_function/mobilenet_v1.py models/research/slim/nets/')
os.system('cp -f utility_function/visualization_utils.py models/research/object_detection/utils/') 
