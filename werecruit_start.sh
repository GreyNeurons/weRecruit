#!/bin/bash

echo "Starting web app"
nohup python3 ./src/werecruit/webApp.py & #wr_webapp

echo "Starting scheduler"
nohup python3 ./src/werecruit/cronjobs.py & #wr_sched

echo 
echo "weRecruit started."



