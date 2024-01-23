#!/bin/bash

cd /home/ec2-user/
/bin/bash /home/ec2-user/scripts/prepare_data.sh || exit 1
nohup python3 dash_app/app.py --JenkinsJobs data/jenkins_jobs.csv  --JobDetails data/job_details.csv &