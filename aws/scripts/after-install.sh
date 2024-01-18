#!/bin/bash
set -xe
echo "after-install.sh"
ls
# Copy war file from S3 bucket to tomcat webapp folder
#aws s3 cp s3://xfirefabanalyzerstack-webappdeploymentbucket-4hzzfft9vosf/xfire_fabrication_analyzer.zip /usr/local/xfire_fabrication_analyzer.zip
#unzip /usr/local/xfire_fabrication_analyzer.zip -d /usr/local/xfire_fabrication_analyzer

# Ensure the ownership permissions are correct.
#chown -R tomcat:tomcat /usr/local/tomcat9/webapps