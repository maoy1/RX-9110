#!/bin/bash
set -xe
echo "application-start.sh"

# Start Tomcat, the application server.
#service tomcat start
pwd
ls
nohup python xfire-fabrication-process-analyzer/xfire_fabrication_dashboard.py &
exit 1