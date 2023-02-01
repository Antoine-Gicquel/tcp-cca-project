#!/bin/bash

TEST_PATH="$1"
MAX_USERS="$2"

NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

echo "Loading test $TEST_PATH"
echo "Clearing previous results"
sudo rm ./users/results/*.json 2>/dev/null
sudo rm ./users/config/*.cfg 2>/dev/null

echo "Setting up the containers config files..."
# Setup the .cfg files
sudo ./utils/setup_containers_configs.sh $TEST_PATH


echo "Setting up Traffic Control (Network Emulation)..."
# TODO Setup tcconfig
./utils/setup_tcconfig.sh $TEST_PATH

echo "Done ! Sending signal to start tests"
touch ./shared/lock_test

echo "Waiting for tests to finish..."
# wait for test

while [ $(ls ./shared/ready | wc -l) -lt $MAX_USERS ]
do
    sleep 2
done

sudo rm ./shared/ready/* 2>/dev/null



echo "Exporting results..."
# parse results
sudo rm -rf $TEST_PATH/results 2>/dev/null
mkdir $TEST_PATH/results

mv ./users/results/*.json $TEST_PATH/results/

echo "==============================="
