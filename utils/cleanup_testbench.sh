#!/bin/bash

sudo docker compose -p testbench down
sudo rm ./users/results/*.json
sudo rm ./users/config/*.cfg
sudo rm ./shared/ready/*
 
python3 ./utils/reset_sg.py

echo "Testbench has been reset"