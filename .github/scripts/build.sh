#!/bin/bash
set -xe

# Maven is used to build  and create a war file.
#mvn -Dmaven.test.skip=true clean install
zip -r xfire_fabrication_analyzer.zip requirements.txt  xfire-fabrication-process-analyzer aws


