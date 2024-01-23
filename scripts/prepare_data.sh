#!/bin/bash -x
workdir0=$(dirname $0)
workdir="$(dirname "$workdir0")"
job_file=${1-"data/jenkins_jobs.csv"}
detail_file=${2-"data/job_details.csv"}
data_folder="data"

cd $workdir
aws s3 sync s3://xfirefabanalyzerstack-webappdeploymentbucket-gguw7zonzjwy/data/ input || exit 1
if [[ -d $data_folder ]]
then
  rm -rf $data_folder/* || exit 2
else 
  mkdir $data_folder
fi
# extract jobs detail of substeps duration
python3 ./dash_app/extract_xfrun_log.py --InputDir "input/xfrun" --Output "$detail_file" || exit 3

# extract "start db fabrication" phases duration
python3 ./dash_app/extract_start_db_jenkins_build_xml.py --InputDir "input/builds" --Output "$job_file" || exit 4
