#!/bin/bash

TEST_PATH=$1


NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

NB_USERS=$(echo $NODES | jq -M .count)


# config files
rm ./users/config/*.cfg 2>/dev/null || true
for ((c=1; c<=$NB_USERS; c++)); do
    USER_CONFIG=$(echo $NODES | jq -M .\"$((c + 100))\")
    if [ $(echo $USER_CONFIG | grep "^null\$" | wc -l) -ge 1 ]
    then
        USER_CONFIG=$(echo $NODES | jq -M .default_settings)
    fi
    echo $USER_CONFIG > ./users/config/$((c + 100)).cfg
done
