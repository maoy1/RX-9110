import glob
import os
import argparse
import re
from datetime import datetime, timedelta

import pandas as pd

parser = argparse.ArgumentParser(description="extract xfrun log arguments")
parser.add_argument(
    "--InputDir",
    help="Input file to extract xfrun log",
    required=False,
    default="C:\\projects\\small_projects\\PythonDash-CICOTemplate\\input\\xfrun",
)
parser.add_argument(
    "--Output",
    help="The Jenkins Job CSV data file",
    required=False,
    default="C:\\projects\\small_projects\\PythonDash-CICOTemplate\\data\\job_details.csv",
)
argument = parser.parse_args()
input_dir = argument.InputDir
output_file = argument.Output


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

# Define regular expressions for BEGIN and ENDED steps
begin_pattern = re.compile(r"(.*).errlog:BEGIN ([\.|\w]+) (.*)")
ended_pattern = re.compile(r"(.*).errlog:ENDED ([\.|\w]+) (.*)( Duration |, )(\d+)")
sub_ended_pattern = re.compile(r"(.*).errlog:ended (\w+): (.*), (\d+), (\d+)")

steps = []
step_stack = []
batches_main_step = []

# Extract the steps and their relationships
def extract_content(content):
    global steps
    global step_stack
    global batches_main_step
    batch_comp = ""
    for line in content.splitlines():
        begin_match = begin_pattern.search(line)
        ended_match = ended_pattern.search(line)
        sub_ended_match = sub_ended_pattern.search(line)

        if begin_match:
            step_batch = begin_match.group(1)
            if step_batch != batch_comp:
                # new batch
                batch_comp = step_batch
                if len(steps) > 0:
                    batches_main_step.append(steps[0])
                steps = []
                step_stack = []
            step_name = begin_match.group(2)
            #print ("step_name", step_name)
            # workaround: ignore get_cmp.sh, since no ENDED line for it"
            if step_name == "get_cmp.sh":
                continue
            step_start_time = begin_match.group(3)
            if step_start_time.find("-") < 0:
                # no sub step just timestamp
                step_start_time = datetime.strptime(
                    step_start_time, "%a %b %d %H:%M:%S %Z %Y"
                ).strftime("%Y-%m-%dT%H:%M:%S")
            else:
                step_start_time = step_start_time.split(" ")[-1]
                step_start_time = step_start_time.split("+")[0]
                step_start_time = datetime.strptime(
                    step_start_time, "%Y-%m-%dT%H:%M:%S"
                ).strftime("%Y-%m-%dT%H:%M:%S")

            step = {
                "batch": step_batch,
                "name": step_name,
                "start_time": step_start_time,
                "children": [],
            }
            #print ("step start", step)
            if step_stack:
                step_stack[-1]["children"].append(step)

            step_stack.append(step)
            steps.append(step)
        elif ended_match:
            step_name = ended_match.group(2)
            step_end_time = ended_match.group(3)
            duration = float(ended_match.group(5))

            if step_end_time:
                if step_end_time.find("-") > 0:
                    step_end_time = step_end_time.split(" ")[-1]
                    step_end_time = step_end_time.split("+")[0]
                    step_end_time = datetime.strptime(
                        step_end_time, "%Y-%m-%dT%H:%M:%S"
                    ).strftime("%Y-%m-%dT%H:%M:%S")
                else:
                    step_end_time = datetime.strptime(
                        step_end_time, "%a %b %d %H:%M:%S %Z %Y"
                    ).strftime("%Y-%m-%dT%H:%M:%S")

            step = step_stack.pop()
            step["end_time"] = step_end_time
            step["duration"] = duration
            #print ("step end", step)
        elif sub_ended_match:
            step_batch = sub_ended_match.group(1)
            step_name = f":{sub_ended_match.group(2)}"
            step_end_time = sub_ended_match.group(3)
            duration = float(sub_ended_match.group(4))
            if step_end_time:
                step_end_time = end_time = datetime.strptime(
                    step_end_time, "%Y-%m-%dT%H:%M:%S"
                )
            step_start_time = step_end_time - timedelta(seconds=duration)
            step = {
                "batch": step_batch,
                "name": step_name,
                "start_time": step_start_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "end_time": step_end_time.strftime("%Y-%m-%dT%H:%M:%S"),
                "duration": duration,
            }
            #print ("sub step end", step)
            if step_stack:
                step_stack[-1]["children"].append(step)
            steps.append(step)

# Print the extracted steps and relationships
# for step in steps:
#    print(step)



# Flatten the nested steps
def flatten_steps(steps, parent=None):
    flattened = []
    for step in steps:
        step["isLeaf"] = True
        if parent:
            step["parent"] = parent["name"]
            parent["isLeaf"] = False
        if "duration" in step:
            step["duration_string"] = seconds_to_duration(step["duration"])
        else:
            step["duration_string"] = ""
        flattened.append(step)
        flattened.extend(flatten_steps(step.pop("children", []), step))
    return flattened




content = None
filelist=out_files = sorted(glob.glob(os.path.join(input_dir, "*_xfrun_errlog.log")))
print ("filelist", filelist)
for file in filelist:
    with open(file, encoding="utf-8") as f:
        extract_content(f.read())

if len(steps) > 0:
    batches_main_step.append(steps[0])
# for batch in batchs_main_step:
#    print(batch)


flattened_steps = flatten_steps(batches_main_step)

# for f in flattened_steps:
#    print (f)

pd.DataFrame(flattened_steps).to_csv(
    output_file,
    columns=[
        "batch",
        "name",
        "start_time",
        "end_time",
        "duration",
        "duration_string",
        "parent",
        "isLeaf",
    ],
)
