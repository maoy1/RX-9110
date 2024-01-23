import argparse
import csv
import fnmatch
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta

parser = argparse.ArgumentParser(description="Extract db fabrication data arguments")
parser.add_argument(
    "--InputDir",
    help="Input file to extract Jenkins Job file",
    required=False,
    default="C:\\projects\\small_projects\\PythonDash-CICOTemplate\\input",
)
parser.add_argument(
    "--Output",
    help="The Jenkins Job CSV data file",
    required=False,
    default="C:\\projects\\small_projects\\RX-9110\\data\\jenkins_jobs.csv",
)
argument = parser.parse_args()
input_dir = argument.InputDir
output_file = argument.Output

def duration_to_seconds(duration_str):
    units = {"day": 86400, "hr": 3600, "min": 60, "sec": 1}
    parts = re.findall(r"(\d+(?:\.\d+)?)\s*(day|hr|min|sec)", duration_str)
    return sum(float(value) * units[unit] for value, unit in parts)


def seconds_to_duration(seconds):
    days, remainder1 = divmod(seconds, 86400)
    hours, remainder = divmod(remainder1, 3600)
    minutes, seconds = divmod(remainder, 60)
    duration_str = ""
    if days > 0:
        duration_str += f"{int(days)} day "
    if hours > 0:
        duration_str += f"{int(hours)} hr "
    if minutes > 0:
        duration_str += f"{int(minutes)} min "
    if seconds > 0:
        duration_str += f"{seconds:.1f} sec"
    return duration_str.strip()


filelist_tuple = []
for dirpath, dirnames, filenames in os.walk(input_dir):
    for filename in fnmatch.filter(filenames, "build.xml"):
        file_path = os.path.join(dirpath, filename)
        file_folder = os.path.dirname(file_path)
        buildnr = os.path.basename(file_folder)
        modify_time = os.path.getmtime(file_path)
        modify_date = time.strftime("%Y-%m-%d", time.localtime(modify_time))
        filelist_tuple.append((modify_date, buildnr, file_path))
sorted_filelist = sorted(filelist_tuple, key=lambda x: int(x[1]))

data = []
for modify_date, buildnr, file_path in sorted_filelist:
    # tree = ET.parse("RX-9110/2023-10-25a_rx_fx_jenkins_jenkins_jobs/jobs/start db fabrication/builds/7/build.xml")
    tree = ET.parse(file_path)
    root = tree.getroot()
    dbnr = ""
    # get db number
    for sub_build in root.findall(".//hudson.model.TextParameterValue"):
        if sub_build.find("name").text == "dbnum":
            dbnr = sub_build.find("value").text
            break

    # get xfrun start, stop time and duration
    starttime = root.find("startTime").text
    duration_all = float(root.find("duration").text) / 1000
    start_time = datetime.fromtimestamp(float(starttime) / 1000)
    # end_time=start_time+timedelta(seconds=float(duration_all)/1000)

    end_time = start_time
    # phases are sequential, suppose the phases are ordered
    pre_phase = ""
    max_duration = 0.0
    batchname = f"{modify_date}_xf{dbnr}_xfrun_build{buildnr}"
    data.append(
        (
            batchname,
            "",
            "complete",
            "db fabrication",
            start_time.isoformat(),
            (start_time + timedelta(seconds=duration_all)).isoformat(),
            duration_all,
            seconds_to_duration(duration_all),
        )
    )
    for sub_build in root.findall(
        ".//com.tikal.jenkins.plugins.multijob.MultiJobBuild_-SubBuild"
    ):
        parent_job_name = sub_build.find("parentJobName")
        phase_name = sub_build.find("phaseName")
        job_name = sub_build.find("jobName")
        duration_str = sub_build.find("duration")
        if (
            duration_str is None
            or parent_job_name is None
            or job_name is None
            or phase_name is None
        ):
            continue
        if duration_str.text is None:
            duration = 0
        else:
            duration = float(duration_to_seconds(duration_str.text))
        if pre_phase != phase_name.text:
            pre_phase = phase_name.text
            start_time = start_time + timedelta(seconds=max_duration)
            # end_time = start_time + timedelta(seconds = duration)
            max_duration = 0
        if duration > max_duration:
            max_duration = duration
        # data.append((parent_job_name.text, phase_name.text, job_name.text, duration_to_seconds(duration.text), duration.text))
        data.append(
            (
                batchname,
                parent_job_name.text,
                phase_name.text,
                job_name.text,
                start_time.isoformat(),
                (start_time + timedelta(seconds=duration)).isoformat(),
                duration,
                duration_str.text,
            )
        )

with open(output_file, "w", newline="") as csvfile:
    csv_writer = csv.writer(csvfile)
    csv_writer.writerow(
        [
            "batch",
            "parent",
            "phase",
            "name",
            "start_time",
            "end_time",
            "duration",
            "duration_string",
        ]
    )  # Write header row
    csv_writer.writerows(data)  # Write data rows
