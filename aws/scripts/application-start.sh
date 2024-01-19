#!/bin/bash
set -xe
echo "application-start.sh"

# Start Tomcat, the application server.
#service tomcat start

sudo systemctl daemon-reload
sudo systemctl start xfire-fab-analyser
sudo systemctl status xfire-fab-analyser
