from subprocess import Popen, PIPE
import sys
import os
'''
out, err = Popen('ls | grep venv', shell=True, stdout=PIPE).communicate()
#print out
if out == 'venv\n':
    print ('Venv error...')
    sys.exit()


Popen('virtualenv --system-site-packages -p python2.7 ./venv', shell=True, stdout=PIPE).communicate()
print ('Venv done')
'''

out, err = Popen('pip list | grep tensorflow-', shell=True, stdout=PIPE).communicate()

print ('--not venv--')
print out
print err
print ('--')

Popen(["venv/bin/python","setup_lib.py"])
'''
out, err = Popen('source ./venv/bin/activate', shell=True, stdout=PIPE).communicate()
print ('--')
print out
print err
print ('--')
'''


out, err = Popen('pip list | grep tensorflow-', shell=True, stdout=PIPE).communicate()
print ('--not venv--')
print out
print err
print ('--')
'''
out, err = Popen('pip install --upgrade pip', shell=True, stdout=PIPE).communicate()
print out
print err
print ('--')
'''
