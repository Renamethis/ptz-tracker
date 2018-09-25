from subprocess import Popen, PIPE
import sys
import os

out, err = Popen('pip list | grep tensorflow-', shell=True, stdout=PIPE).communicate()
print ('--venv--')
print out
print err
print ('--')