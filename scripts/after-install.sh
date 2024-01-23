#!/bin/bash

pip3 install -r /home/ec2-user/scripts/requirements.txt

/bin/bash /home/ec2-user/scripts/prepare_data.sh /home/ec2-user/data/jenkins_jobs.csv /home/ec2-user/data/job_details.csv