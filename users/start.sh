#!/bin/bash

inotifywait -e attrib /shared/lock_hostname

ID=$(hostname)
ID="${ID:3}"

while true
do
    echo "Waiting for a test to be ready"
    inotifywait -e attrib /shared/lock_test
    echo "Test starting"
    python3 /app/iperf.py
    echo "Test finished"
    touch /shared/ready/$ID
done
exit 0
