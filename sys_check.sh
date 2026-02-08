#!/bin/bash

echo "Date & Time: $(date)" > log.txt
echo "Disk Usage:" >> log.txt
df -h >> log.txt
echo "Logged-in User: $(whoami)" >> log.txt

if [ ! -d "deploy_app" ]; then
  mkdir deploy_app
fi

mv log.txt deploy_app/

