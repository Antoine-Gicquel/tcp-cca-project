import logging
import json
import os
import random
import copy
import sys

logging.basicConfig(level=logging.INFO)
with open("./utils/secrets/secrets.json", "r") as f:
    SECRETS = json.load(f)


# Small Config (for tests)
tcp_ccas = ["bbr", "reno", "cubic", "infinity"]
qdiscs = ["pfifo_fast", "red", "sfb", "choke", "fq", "codel", "fq_codel"]
regions = SECRETS["regions_full"]
region_ip = regions["tokyo"]
nb_adversaries = 4
average_calculation = 4


if len(sys.argv) != 2:
    print("Usage : generate_tests_qdisc.py <tests_path>")
tests_root = sys.argv[1]


links_default = {
    "backbone": {
        "rate": "10Gbps"
    }
}

nodes_default = {
    "count": 0,
    "default_settings": {
        "cca": "cubic",
        "start_delay": 0,
        "server_ip": "172.20.20.101",
        "server_port": 5501
    }
}

user_default = {
    "cca": "infinity",
    "start_delay": 0,
    "server_ip": "172.20.20.101",
    "server_port": 5201
}


def write_test(alg, adversary, qdisc, index):
    test_path = f"{ tests_root }/{ adversary }/{ qdisc }/{ index }"
    os.makedirs(test_path, exist_ok=True)
    os.makedirs(f"{ test_path }/results", exist_ok=True)
    links = copy.deepcopy(links_default)
    nodes = copy.deepcopy(nodes_default)
    links["backbone"]["qdisc"] = qdisc
    nodes["count"] = nb_adversaries+1
    # On définit le premier user
    user = copy.deepcopy(user_default)
    user["cca"] = alg
    user["server_ip"] = region_ip
    user["server_port"] = 5201 # CHANGER ICI LE PORT DU SERVEUR IPERF DE L'UTILISATEUR TEST
    nodes["101"] = user
    # Puis on définit les n users "adversaires"
    for i in range(1, nb_adversaries+1):
        node_id = str(101+i)
        user = copy.deepcopy(user_default)
        user["cca"] = adversary
        user["server_ip"] = region_ip
        user["server_port"] = 5201+i # CHANGER ICI LES PORTS DES SERVEURS IPERF DES UTILISATEURS "ADVERSAIRES"
        nodes[node_id] = user

    # Enfin, on écrit les configuration dans les bons fichiers
    with open(f"{ test_path }/links.json", "w+") as f:
        f.write(json.dumps(links, indent=4))
    with open(f"{ test_path }/nodes.json", "w+") as f:
        f.write(json.dumps(nodes, indent=4))

def generate_tests():
    for adv in tcp_ccas:
        test_against("infinity", adv)

def test_against(alg, adversary):
    for q in qdiscs:
        test_qdisc(alg, adversary, q)

def test_qdisc(alg, adversary, qdisc):
    for i in range(1, average_calculation+1):
        write_test(alg, adversary, qdisc, i)



generate_tests()