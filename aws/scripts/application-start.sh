#!/bin/bash
set -xe
echo "application-start.sh"

# Start Tomcat, the application server.
#service tomcat start
pwd
ls /usr/local/
ls /usr/local/codedeployresources/
nohup python /usr/local/codedeployresources/xfire_fabrication_dashboard.py &
exit 1