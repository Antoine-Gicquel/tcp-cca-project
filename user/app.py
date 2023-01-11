import socket
import requests
import time
import json
from netcat import Netcat


def get_config():
    from netifaces import AF_INET, ifaddresses
    my_ip = ifaddresses("eth0")[AF_INET][0]['addr']
    my_id = my_ip.split('.')[-1]
    config_path = f"/app/config/{ my_id }.cfg"
    r = ""
    try:
        with open(config_path, "r") as f:
            r = f.read()
    except Exception as e:
        r = json.dumps({"error": str(e)})
    return json.loads(r)


print("Hello Client")

print("Waiting for server to be up...")
time.sleep(3)

config = get_config()
print("What is my config ?", config)
if "error" in config.keys() or "cca" in config.keys() and config["cca"].lower() == "none":
    exit(0)

server_ip = config["server_ip"]
server_port = 5000
print("Checking if it is accessible normally")
r = requests.get(f"http://{ server_ip }:{ server_port }/")
print(r.text)

print("Great, it should have worked!")
print("Trying with Netcat class now")

nc = Netcat(server_ip, server_port)
# nc.set_cca("custom")
nc.start()

nc.write(b'GET / HTTP/1.1\r\nHost: server\r\n\r\n')
received = nc.read_until(b'</p>')
print(received)
