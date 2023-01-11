#!/bin/bash

echo "Waiting for signal"

inotifywait -e attrib /shared/lock
echo "Signal received !"

sleep 1
echo "Starting python"
python3 /app/iperf.py

exit 0
# sleep 10000
