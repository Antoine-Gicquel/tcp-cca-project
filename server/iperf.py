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
            r = f.read()
    except Exception as e:
        r = json.dumps({"error": e})
    return json.loads(r)

print("Hello Server")

config = get_config()


iperf_cmdline = ["iperf3", "-s", "-1"]
iperf_cmdline.extend(["-J"])


result = subprocess.run(iperf_cmdline, capture_output=True)

res_json = result.stdout

with open("/app/results/" + str(get_id()) + ".json", "wb+") as f:
    f.write(res_json)

print("Results have been saved")