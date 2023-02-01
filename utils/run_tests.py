import os
import subprocess
import time
import shutil
import json
import sys

nb_dockers = 5
nb_tests = 0
current_tests = 0
if len(sys.argv) != 3:
    print("Usage : run_tests.py <tests_path> <results_path>")

tests_path = sys.argv[1]
save_path = sys.argv[2]


def run_test(p):
    subprocess.run(["./utils/test.sh", p, str(nb_dockers)])
    time.sleep(1)

def recurse_tests(_p, run_real=True):
    global nb_dockers, nb_tests, current_tests
    p = os.path.abspath(_p)
    l = os.listdir(p)
    if "nodes.json" in l and "links.json" in l:
        if run_real:
            print("Progress :", round(100*current_tests / nb_tests, 1), "%")
            run_test(p)
            current_tests += 1
        else:
            nb_tests += 1
            with open(f"{ p }/nodes.json", "r") as f:
                nb_dockers = max(nb_dockers, json.load(f)["count"])
    elif True in [os.path.isdir(os.path.join(p, x)) for x in l]:
        for x in l:
            if os.path.isdir(os.path.join(p, x)):
                recurse_tests(os.path.join(p, x), run_real)

def save_results(_tests_path, _save_path):
    shutil.copytree(_tests_path, _save_path)


# MAIN

# On initialise nb_dockers
recurse_tests(tests_path, run_real=False)

subprocess.run(["./utils/init_testbench.sh", str(nb_dockers)])

recurse_tests(tests_path, run_real=True)
save_results(tests_path, save_path)

subprocess.run(["./utils/cleanup_testbench.sh"])