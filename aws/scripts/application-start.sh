#!/bin/bash
set -xe
echo "application-start.sh"

# Start Tomcat, the application server.
#service tomcat start

sudo systemctl daemon-reload
sleep 60
sudo systemctl start xfire-fab-analyser
sleep 60
sudo systemctl status xfire-fab-analyser
sleep 60
