#!/bin/bash

TEST_PATH="$1"

NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

NB_USERS=$(echo $NODES | jq -M .users.count)
NB_SERVERS=$(echo $NODES | jq -M .servers.count)

echo "Loading test $TEST_PATH"
echo "Clearing previous results"
rm ./*/results/*.json

echo "Setting up the containers config files..."
# Setup the .cfg files
./utils/setup_containers_configs.sh $TEST_PATH

echo "Opening host firewall..."
# Setup the host firewall rules
./utils/setup_firewall.sh

echo "Booting the containers..."
# Launch the lab
docker compose up --scale usr=$NB_USERS --scale srv=$NB_SERVERS --detach
sleep 2

echo "Setting the IP routes inside the containers..."
# Setup container addresses and routes
./utils/setup_routes.sh

echo "Setting up Traffic Control (Network Emulation)..."
# Setup tcconfig
./utils/setup_tcconfig.sh $TEST_PATH

echo "Done ! Sending signal to start tests"
touch ./shared/lock

echo "Waiting for tests to finish..."
# wait for test

while [ $(docker compose ps -q --status running | wc -l) -gt 2 ]
do
    sleep 5
done

echo "Tests are over, shutting down the lab..."
# bring lab down
docker compose down

echo "Exporting results..."
# parse results
rm -rf $TEST_PATH/results
mkdir $TEST_PATH/results
mkdir $TEST_PATH/results/users
mkdir $TEST_PATH/results/servers

mv ./user/results/*.json $TEST_PATH/results/users/
mv ./server/results/*.json $TEST_PATH/results/servers/

