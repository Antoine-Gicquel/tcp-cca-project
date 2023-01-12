import os
import subprocess
import time

def run_test(p):
    print("Running test " + p)
    subprocess.run(["./utils/test.sh", p])
    time.sleep(3)

def recurse_tests(_p):
    p = os.path.abspath(_p)
    l = os.listdir(p)
    if "nodes.json" in l and "links.json" in l:
        run_test(p)
    elif True in [os.path.isdir(os.path.join(p, x)) for x in l]:
        for x in l:
            if os.path.isdir(os.path.join(p, x)):
                recurse_tests(os.path.join(p, x))

recurse_tests("./tests")