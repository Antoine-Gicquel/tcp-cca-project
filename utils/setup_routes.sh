#!/bin/bash

# On compte les conteneurs "usr"
clients=$(docker compose ps | grep "usr" | wc -l)
echo "Detected $clients clients"

servers=$(docker compose ps | grep "srv" | wc -l)
echo "Detected $servers servers"

for ((c=1; c<=$clients; c++)); do
    docker compose exec --index "$c" usr ip a flush dev eth0
    docker compose exec --index "$c" usr ip a add 172.20.10.$((c + 100))/24 dev eth0
    docker compose exec --index "$c" usr ip r add default via 172.20.10.1 dev eth0
    docker compose exec --index "$c" usr ip r add 172.20.20.0/24 via 172.20.10.2 dev eth0
    docker compose exec --index "$c" usr ip r add 172.20.250.0/24 via 172.20.10.2 dev eth0
done

# Routage sur les routeurs
docker compose exec r1 ip r add 172.20.20.0/24 via 172.20.250.3 dev eth0
docker compose exec r2 ip r add 172.20.10.0/24 via 172.20.250.2 dev eth0

for ((s=1; s<=$servers; s++)); do
    docker compose exec --index "$s" srv ip a flush dev eth0
    docker compose exec --index "$s" srv ip a add 172.20.20.$((s + 100))/24 dev eth0
    docker compose exec --index "$s" srv ip r add default via 172.20.20.1 dev eth0
    docker compose exec --index "$s" srv ip r add 172.20.10.0/24 via 172.20.20.2 dev eth0
    docker compose exec --index "$s" srv ip r add 172.20.250.0/24 via 172.20.20.2 dev eth0
done