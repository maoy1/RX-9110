#!/bin/bash
set -xe

# Maven is used to build  and create a war file.
#mvn -Dmaven.test.skip=true clean install
zip -r xfire_process_analyzer.zip *.py


