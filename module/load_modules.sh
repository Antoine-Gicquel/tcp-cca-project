#!/bin/bash

echo "Loading BBR"
sudo modprobe tcp_bbr

echo "Loading Infinity"
cd infinity;
sudo make remove
make clean && make && sudo make insert
cd ..