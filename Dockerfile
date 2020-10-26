FROM python:2
WORKDIR ../ptztracker/
COPY setup.sh .
COPY get-pip.py .
RUN ["/bin/bash", "-f", "setup.sh"]
CMD [ "python2", "start_tracker.py"]
COPY . .
