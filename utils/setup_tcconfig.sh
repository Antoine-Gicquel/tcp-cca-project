#!/bin/bash


TEST_PATH=$1


NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

NB_USERS=$(echo $NODES | jq -M .users.count)
NB_SERVERS=$(echo $NODES | jq -M .servers.count)


# Pour obtenir l'interface côté hôte qui correspond à une interface du docker
get_interface () {
    CONTAINER=$1
    INTERFACE=$2
    IF_ID=$(docker compose exec $CONTAINER ip -o l show dev $INTERFACE | awk -F': ' '{ print $2 }' | awk -F'@if' '{ print $2 }')
    RET_VAL=$(ip -o link | grep -E "^$IF_ID:" | awk -F': ' '{ print $2 }' | awk -F'@if' '{ print $1 }')
    echo $RET_VAL
}

apply_config () {
    INTERFACE=$1
    CONFIG_NAME=$2
    tcdel $INTERFACE --all 1>/dev/null 2>/dev/null
    COMMAND=""
    DELAY=$(echo $LINKS | jq -M --raw-output .$CONFIG_NAME.delay)
    RATE=$(echo $LINKS | jq -M --raw-output .$CONFIG_NAME.rate)
    LOSS=$(echo $LINKS | jq -M --raw-output .$CONFIG_NAME.loss)
    if [ $(echo $DELAY | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        COMMAND="$COMMAND --delay $DELAY"
    fi
    if [ $(echo $RATE | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        COMMAND="$COMMAND --rate $RATE"
    fi
    if [ $(echo $LOSS | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        COMMAND="$COMMAND --loss $LOSS"
    fi

    # If config is not backbone, set both incoming and outgoing
    if [ $(echo $CONFIG_NAME | grep -E "^backbone\$" | wc -l) -eq 0 ]
    then
        tcset $INTERFACE --direction incoming $COMMAND
    fi
    tcset $INTERFACE --direction outgoing $COMMAND
}



################################################
################## BACKBONE ####################
################################################

R1_ETH0=$(get_interface r1 eth0)
R2_ETH0=$(get_interface r2 eth0)
# TODO appliquer les règles qui sont dans le links.json
apply_config $R1_ETH0 "backbone"
apply_config $R2_ETH0 "backbone"


################################################
################## DEFAULTS ####################
################################################

DEFAULT_USER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .users.default_settings.link)
if [ $(echo $DEFAULT_USER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
then
    for ((c=1; c<=$NB_USERS; c++)); do
        INTERFACE=$(get_interface "--index $c usr" eth0)
        apply_config $INTERFACE $DEFAULT_USER_LINK_CONFIG
    done
fi

# TODO appliquer la règle par défaut sur les servers
DEFAULT_SERVER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .servers.default_settings.link)
if [ $(echo $DEFAULT_SERVER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
then
    for ((s=1; s<=$NB_SERVERS; s++)); do
        INTERFACE=$(get_interface "--index $s srv" eth0)
        apply_config $INTERFACE $DEFAULT_SERVER_LINK_CONFIG
    done
fi


################################################
################## SPECIFICS ###################
################################################

# Users
for ((c=1; c<=$NB_USERS; c++)); do
    USER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .users.\"$((c + 100))\".link)
    if [ $(echo $USER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        INTERFACE=$(get_interface "--index $c usr" eth0)
        apply_config $INTERFACE $USER_LINK_CONFIG
    fi
done
# same for servers
for ((s=1; s<=$NB_SERVERS; s++)); do
    SERVER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .servers.\"$((s + 100))\".link)
    if [ $(echo $SERVER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        INTERFACE=$(get_interface "--index $s srv" eth0)
        apply_config $INTERFACE $SERVER_LINK_CONFIG
    fi
done
