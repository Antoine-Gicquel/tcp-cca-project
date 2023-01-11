#!/bin/bash

TEST_PATH=$1


NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

NB_USERS=$(echo $NODES | jq -M .users.count)
NB_SERVERS=$(echo $NODES | jq -M .servers.count)


# config files
rm ./user/config/*.cfg
for ((c=1; c<=$NB_USERS; c++)); do
    USER_CONFIG=$(echo $NODES | jq -M .users.\"$((c + 100))\")
    if [ $(echo $USER_CONFIG | grep "^null\$" | wc -l) -ge 1 ]
    then
        USER_CONFIG=$(echo $NODES | jq -M .users.default_settings)
    fi
    echo $USER_CONFIG > ./user/config/$((c + 100)).cfg
done
# same for servers
rm ./server/config/*.cfg
for ((s=1; s<=$NB_SERVERS; s++)); do
    SERVER_CONFIG=$(echo $NODES | jq -M .servers.\"$((s + 100))\")
    if [ $(echo $SERVER_CONFIG | grep -E "^null\$" | wc -l) -ge 1 ]
    then
        SERVER_CONFIG=$(echo $NODES | jq -M .servers.default_settings)
    fi
    echo $SERVER_CONFIG > ./server/config/$((s + 100)).cfg
done
