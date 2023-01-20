#!/bin/bash

modules=$(ls -d */)

for m in $modules
do
  echo Loading $m
  cd $m && make clean && make && sudo make insert
  cd ..
done