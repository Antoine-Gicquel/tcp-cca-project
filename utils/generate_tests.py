import logging
import json
import os
import random
import copy

logging.basicConfig(level=logging.INFO)
# run_id = hex(random.getrandbits(32))[2:]
with open("./utils/secrets/secrets.json", "r") as f:
    SECRETS = json.load(f)


# Full Config
tcp_ccas = ["bbr", "hybla", "infinity", "vegas", "veno", "westwood", "cubic"]
regions = SECRETS["regions_full"] # {"paris": "paris_server_ip", "frankfurt": "frankfurt_server_ip", ...}
max_adversaries = 5

# Small Config (for tests)
tcp_ccas = ["cubic", "bbr", "infinity"]
regions = SECRETS["regions"]
max_adversaries = 3




links_default = {
    "backbone": {
        "rate": "10Gbps"
    }
}

nodes_default = {
    "servers": {
        "count": 0,
        "default_settings": {
            "cca": "cubic",
            "start_delay": 0
        }
    },
    "users": {
        "count": 0,
        "default_settings": {
            "cca": "cubic",
            "start_delay": 0,
            "server_ip": "172.20.20.101",
            "server_port": 5501
        }
    }
}

user_default = {
    "cca": "infinity",
    "start_delay": 0,
    "server_ip": "172.20.20.101",
    "server_port": 5201
}


for c in tcp_ccas:
    os.mkdir(f"./tests/auto-{ c }")
    for o_c in tcp_ccas:
        os.mkdir(f"./tests/auto-{ c }/{ o_c }")
        for r in regions:
            os.mkdir(f"./tests/auto-{ c }/{ o_c }/{ r }")
            for n in range(1, max_adversaries+1):
                os.mkdir(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }")
                os.mkdir(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }/results")
                os.mkdir(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }/results/servers")
                os.mkdir(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }/results/users")
                links = copy.deepcopy(links_default)
                nodes = copy.deepcopy(nodes_default)
                nodes["users"]["count"] = n+1
                # On définit le premier user
                user = copy.deepcopy(user_default)
                user["cca"] = c
                user["server_ip"] = regions[r]
                user["server_port"] = 5201 # CHANGER ICI LE PORT DU SERVEUR IPERF DE L'UTILISATEUR TEST
                nodes["users"]["101"] = user
                # Puis on définit les n users "adversaires"
                for i in range(1, n+1):
                    node_id = str(101+i)
                    user = copy.deepcopy(user_default)
                    user["cca"] = o_c
                    user["server_ip"] = regions[r]
                    user["server_port"] = 5201+i # CHANGER ICI LES PORTS DES SERVEURS IPERF DES UTILISATEURS "ADVERSAIRES"
                    nodes["users"][node_id] = user

                # Enfin, on écrit les configuration dans les bons fichiers
                with open(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }/links.json", "w+") as f:
                    f.write(json.dumps(links, indent=4))
                with open(f"./tests/auto-{ c }/{ o_c }/{ r }/{ n }/nodes.json", "w+") as f:
                    f.write(json.dumps(nodes, indent=4))


