#!/bin/bash


TEST_PATH=$1


NODES=$(cat $TEST_PATH/nodes.json)
LINKS=$(cat $TEST_PATH/links.json)

NB_USERS=$(echo $NODES | jq -M .count)


# Pour obtenir l'interface côté hôte qui correspond à une interface du docker
get_interface () {
    CONTAINER=$1
    INTERFACE=$2
    IF_ID=$(docker compose -p testbench exec $CONTAINER ip -o l show dev $INTERFACE | awk -F': ' '{ print $2 }' | awk -F'@if' '{ print $2 }')
    RET_VAL=$(ip -o link | grep -E "^$IF_ID:" | awk -F': ' '{ print $2 }' | awk -F'@if' '{ print $1 }')
    echo $RET_VAL
}

apply_config_netem () {
    INTERFACE=$1
    CONFIG_NAME=$2
    tcdel $INTERFACE --all 2>/dev/null 1>/dev/null
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

    if [ -n "$COMMAND" ]
    then
        echo "Applying netem $COMMAND to $INTERFACE"
        # # If config is not backbone, set both incoming and outgoing
        # if [ $(echo $CONFIG_NAME | grep -E "^backbone\$" | wc -l) -eq 0 ]
        # then
        #     tcset $INTERFACE --direction incoming $COMMAND
        # fi
        tcset $INTERFACE --direction outgoing $COMMAND
    fi
}

apply_config_qdisc () {
    INTERFACE=$1
    CONFIG_NAME=$2
    tcdel $INTERFACE --all 1>/dev/null 2>/dev/null
    QDISC=$(echo $LINKS | jq -M --raw-output .$CONFIG_NAME.qdisc)
    if [ -n $QDISC ]
    then
        echo "Applying qdisc $QDISC to $INTERFACE"
        tc qdisc del dev $INTERFACE root 2>/dev/null
        tc qdisc add dev $INTERFACE root $QDISC
        echo "$QDISC was set !"
        tc qdisc show dev $INTERFACE root
        # Applying qdisc choke to vethae5f1a9
        # Required parameter (bandwidth, limit) is missing
        # Applying qdisc red to vethae5f1a9
        # RED: Required parameter (limit, avpkt) is missing
    fi
}


################################################
################## DEFAULTS ####################
################################################

DEFAULT_USER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .default_settings.link)
if [ $(echo $DEFAULT_USER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
then
    for ((c=1; c<=$NB_USERS; c++)); do
        INTERFACE=$(get_interface "--index $c usr" eth0)
        echo "Applying $DEFAULT_USER_LINK_CONFIG to user $c"
        apply_config_netem $INTERFACE $DEFAULT_USER_LINK_CONFIG
    done
fi


################################################
################## SPECIFICS ###################
################################################

# Users
for ((c=1; c<=$NB_USERS; c++)); do
    USER_LINK_CONFIG=$(echo $NODES | jq -M --raw-output .\"$((c + 100))\".link)
    if [ $(echo $USER_LINK_CONFIG | grep -E "^null\$" | wc -l) -eq 0 ]
    then
        INTERFACE=$(get_interface "--index $c usr" eth0)
        echo "Applying $USER_LINK_CONFIG to user $c"
        apply_config_netem $INTERFACE $USER_LINK_CONFIG
    fi
done


# Backbone

ROUTER_QDISC_INTERFACE=$(get_interface router-qdisc eth0)
ROUTER_CONGESTION_INTERFACE=$(get_interface router-congestion eth0)
echo "Applying backbone config to router"
apply_config_netem $ROUTER_CONGESTION_INTERFACE backbone
apply_config_qdisc $ROUTER_QDISC_INTERFACE backbone
