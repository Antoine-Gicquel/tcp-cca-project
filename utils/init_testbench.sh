#!/bin/bash

NB_USERS="$1"

echo "Loading congestion control algorithms"
cd module; sudo ./load_modules.sh 2>/dev/null; cd ..

echo "Disabling TCP offloading"
INTERFACE=$(ip -br l | awk '$1 !~ "lo|vir|wl|br" { print $1}' | head -n 1)
sudo ethtool -K $INTERFACE gro off
sudo ethtool -K $INTERFACE gso off
sudo ethtool -K $INTERFACE tcp-segmentation-offload off

echo "Opening EC2 ports"
python3 ./utils/update_sg.py

echo "Setting up host firewall"
sudo ./utils/setup_firewall.sh

echo "Clearing previous results"
sudo rm ./users/results/*.json 2>/dev/null
sudo rm ./users/config/*.cfg 2>/dev/null

echo "Booting the containers..."
# Launch the lab
sudo docker compose -p testbench up --scale usr=$NB_USERS --detach
sleep 2

# Rename the containers to let them know their ID
for I in $(seq 1 $NB_USERS)
do
    sudo docker compose -p testbench exec --index=$I usr hostname usr$I
done

touch ./shared/lock_hostname

echo "Setting the IP routes inside the containers..."
# Setup container addresses and routes
sudo ./utils/setup_routes.sh

echo "The testbench is ready !"
echo "==============================="