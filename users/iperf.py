import time
import json
import subprocess
from netifaces import AF_INET, ifaddresses

def get_id():
    my_ip = ifaddresses("eth0")[AF_INET][0]['addr']
    return my_ip.split('.')[-1]

def get_config():
    my_id = get_id()
    config_path = f"/app/config/{ my_id }.cfg"
    r = ""
    try:
        with open(config_path, "r") as f:
            r = json.loads(f.read())
    except Exception as e:
        print(e)
        return None
    return r

print("Hello Client")

print("Getting config")
config = get_config()

if config == None:
    print("I have no job to do here")
    exit(0)

for k in config.keys():
    try:
        config[k] = config[k].strip()
    except:
        pass

if config['cca'] == "none":
    exit(0)

print("Waiting for server to be up...")
time.sleep(3)

print("CCA to use:", config['cca'])
iperf_cmdline = ["iperf3"]
iperf_cmdline.extend(["-c", config['server_ip']])
if "server_port" in config.keys():
    iperf_cmdline.extend(["-p", str(config['server_port'])])
iperf_cmdline.extend(["-t", "15"])
iperf_cmdline.extend(["--omit", "5"])
iperf_cmdline.extend(["-C", config['cca']])
iperf_cmdline.extend(["-J"])


result = subprocess.run(iperf_cmdline, capture_output=True)

res_json = result.stdout

with open("/app/results/" + str(get_id()) + ".json", "wb+") as f:
    f.write(res_json)

print("Results have been saved")