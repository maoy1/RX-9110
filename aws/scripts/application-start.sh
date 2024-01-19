#!/bin/bash
set -xe
echo "application-start.sh"

# Start Tomcat, the application server.
#service tomcat start
pwd
ls /usr/local/
ls -l /usr/local/codedeployresources/xfire-fabrication-process-analyzer
nohup python /usr/local/codedeployresources/xfire-fabrication-process-analyzer/xfire_fabrication_dashboard.py &
exit 1