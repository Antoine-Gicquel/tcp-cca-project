import logging
import json
import os
import random
import copy
import sys

logging.basicConfig(level=logging.INFO)
with open("./utils/secrets/secrets.json", "r") as f:
    SECRETS = json.load(f)


# Full Config
tcp_ccas = ["bbr", "hybla", "infinity", "vegas", "veno", "westwood", "cubic"]
regions = SECRETS["regions_full"] # {"paris": "paris_server_ip", "frankfurt": "frankfurt_server_ip", ...}
max_adversaries = 5
average_calculation = 5

# Small Config (for tests)
tcp_ccas = ["bbr", "reno", "cubic", "infinity"]
regions = SECRETS["regions"]
max_adversaries = 4
average_calculation = 3


if len(sys.argv) != 2:
    print("Usage : generate_tests.py <tests_path>")
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


def write_test(alg, adversary, region, nb_adv, index):
    test_path = f"{ tests_root }/{ alg }/{ adversary }/{ region }/{ nb_adv }/{ index }"
    os.makedirs(test_path, exist_ok=True)
    os.makedirs(f"{ test_path }/results", exist_ok=True)
    links = copy.deepcopy(links_default)
    nodes = copy.deepcopy(nodes_default)
    nodes["count"] = nb_adv+1
    # On définit le premier user
    user = copy.deepcopy(user_default)
    user["cca"] = alg
    user["server_ip"] = regions[region]
    user["server_port"] = 5201 # CHANGER ICI LE PORT DU SERVEUR IPERF DE L'UTILISATEUR TEST
    nodes["101"] = user
    # Puis on définit les n users "adversaires"
    for i in range(1, nb_adv+1):
        node_id = str(101+i)
        user = copy.deepcopy(user_default)
        user["cca"] = adversary
        user["server_ip"] = regions[region]
        user["server_port"] = 5201+i # CHANGER ICI LES PORTS DES SERVEURS IPERF DES UTILISATEURS "ADVERSAIRES"
        nodes[node_id] = user

    # Enfin, on écrit les configuration dans les bons fichiers
    with open(f"{ test_path }/links.json", "w+") as f:
        f.write(json.dumps(links, indent=4))
    with open(f"{ test_path }/nodes.json", "w+") as f:
        f.write(json.dumps(nodes, indent=4))

def generate_tests():
    for alg in tcp_ccas:
        test_algo(alg)

def test_algo(alg):
    for adv in tcp_ccas:
        test_against(alg, adv)

def test_against(alg, adversary):
    for r in regions:
        test_region(alg, adversary, r)

def test_region(alg, adversary, region):
    for nb_adv in range(1, max_adversaries+1):
        test_nb_adversaries(alg, adversary, region, nb_adv)

def test_nb_adversaries(alg, adversary, region, nb_adv):
    for i in range(1, average_calculation+1):
        test_average(alg, adversary, region, nb_adv, i)

def test_average(alg, adversary, region, nb_adv, index):
    write_test(alg, adversary, region, nb_adv, index)



generate_tests()