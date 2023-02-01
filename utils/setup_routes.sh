#!/bin/bash

# On compte les conteneurs "usr"
clients=$(docker compose -p testbench ps | grep "usr" | wc -l)
echo "Detected $clients clients"

for ((c=1; c<=$clients; c++)); do
    docker compose -p testbench exec --index "$c" usr ip a flush dev eth0
    docker compose -p testbench exec --index "$c" usr ip a add 172.20.10.$((c + 100))/24 dev eth0
    docker compose -p testbench exec --index "$c" usr ip r add default via 172.20.10.2 dev eth0
done

# Routage sur les routeurs
docker compose -p testbench exec router ip r add default via 172.20.11.1 dev eth0
docker compose -p testbench exec router nft insert rule ip nat POSTROUTING oifname "eth0" counter masquerade