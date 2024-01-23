#!/bin/bash
set -xe

# Delete the old  directory as needed.
if [ -d /home/ec2-user ]; then
    rm -rf /home/ec2-user/*
fi
