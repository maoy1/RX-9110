#!/bin/bash
set -x
echo "application-stop.sh"

# System control will return either "active" or "inactive".
SERVICE_FILE=/etc/systemd/system/xfire-fab-analyser.service
if test -f "$SERVICE_FILE"; then
    sudo systemctl stop xfire-fab-analyser.service
    sudo rm "$SERVICE_FILE"
fi