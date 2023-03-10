import os
import json
import matplotlib.pyplot as plt
import numpy as np
import sys
from math import sin, pi


def jain_fairness(seq):
    num = sum(seq) ** 2
    den = len(seq) * sum(map(lambda x: x**2, seq))
    return num/den

def g_fairness(k, seq):
    x_max = max(seq)
    acc = 1
    for x in seq:
        acc *= sin((pi*x)/(2*x_max)) ** (1/k)
    return acc


if len(sys.argv) != 3:
    print("Usage : parse_results_qdisc.py <results_path>")
root_results = sys.argv[1]

results = dict() # results[cca][qdisc] = parse_run_dict

avg = lambda L: sum(L)/len(L)


def parse_run(path):
    print("Parsing", path)
    res = dict()
    users_list = [int(x.split('.')[0]) - 100 for x in os.listdir(f"{ path }/results") if os.path.isfile(f"{ path }/results/{ x }") and x.endswith('.json') and x.split('.')[0].isnumeric()]
    for u in users_list:
        with open(f"{ path }/results/{ 100+u }.json", "r") as f:
            res[u] = json.loads(f.read())["end"]["sum_sent"]
    stats = dict()
    stats["total_traffic"] = sum(res[u]["bytes"] for u in res.keys())
    stats["total_adversary_traffic"] = stats["total_traffic"] - res[1]["bytes"]
    stats["alg_proportion"] = res[1]["bytes"] / [1, stats["total_traffic"]][stats["total_traffic"] > 0]
    stats["jain_fairness"] = jain_fairness([res[u]["bytes"] for u in users_list])
    stats["g1_fairness"] = g_fairness(1, [res[u]["bytes"] for u in users_list])
    res["stats"] = stats
    return res

def parse_average(path):
    runs_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    res_avg = dict()
    for r in runs_list:
        run_path = f"{ path }/{ r }"
        res[r] = parse_run(run_path)
        if not "total_traffic" in res_avg.keys():
            res_avg["total_traffic"] = 0
            res_avg["alg_proportion"] = 0
            res_avg["jain_fairness"] = 0
            res_avg["g1_fairness"] = 0
        res_avg["total_traffic"] += res[r]["stats"]["total_traffic"]
        res_avg["alg_proportion"] += res[r]["stats"]["alg_proportion"]
        res_avg["jain_fairness"] += res[r]["stats"]["jain_fairness"]
        res_avg["g1_fairness"] += res[r]["stats"]["g1_fairness"]
    res_avg["total_traffic"] = int(round(res_avg["total_traffic"]/len(runs_list)/1000000, 0))
    res_avg["alg_proportion"] /= len(runs_list)
    res_avg["jain_fairness"] = res_avg["jain_fairness"] / len(runs_list)
    res_avg["g1_fairness"] = res_avg["g1_fairness"] / len(runs_list)
    res["average"] = res_avg
    return res


def parse_qdiscs(path):
    qdiscs_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for q in qdiscs_list:
        q_path = f"{ path }/{ q }"
        res[q] = parse_average(q_path)
    return res

def parse_algs(path):
    algs_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for alg in algs_list:
        alg_path = f"{ path }/{ alg }"
        res[alg] = parse_qdiscs(alg_path)
    return res

# Plotting part

def plot_alg_on_subplot(ax, x, data):
    bar = []
    bar_label = []
    bar_width = 0.8
    for qdisc in sorted([r for r in data]):
        bar_top = data[qdisc]["average"]["total_traffic"]
        bar_height = data[qdisc]["average"]["g1_fairness"]
        bar.append(bar_height)
        bar_label.append(bar_top)
    rects = ax.bar(x, bar, bar_width)
    plt.bar_label(rects, bar_label)
    return

def plot_alg(fig, alg_id, alg_name, data):
    ax = fig.add_subplot(1, nb_algs, alg_id + 1)
    ax.set_title(f"Tested { alg_name }")
    ax.set_xlabel("Queue discipline")
    ax.set_ylabel("G1 fairness")
    # ax.set_ylim([0, 1])
    x = np.arange(len(data))
    ax.set_xticks(x, sorted([r for r in data]))
    plot_alg_on_subplot(ax, x, data)
    return


def fill_fig(fig, data):
    x = 0
    subplots = []
    for alg in data:
        alg_subplots = plot_alg(fig, x, alg, data[alg])
        x +=1
    return


results = parse_algs(root_results)
nb_algs = len(results)

fig = plt.figure("Tests results for " + root_results)
fig.set_tight_layout(True)
suptitle = root_results + '\n'
suptitle += "G fairness index"
suptitle += "\n(Total traffic in MB on top of column)"
fig.suptitle(suptitle, fontsize=16)
fill_fig(fig, results)

plt.show()