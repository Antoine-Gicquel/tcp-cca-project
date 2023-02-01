import os
import json
import matplotlib.pyplot as plt
import numpy as np
import sys


if len(sys.argv) != 2:
    print("Usage : parse_results.py <results_path>")
root_results = sys.argv[1]

results = dict() # results[cca][adversary][region][number_of_adversaries] = parse_run_dict

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
        res_avg["total_traffic"] += res[r]["stats"]["total_traffic"]
        res_avg["alg_proportion"] += res[r]["stats"]["alg_proportion"]
    res_avg["total_traffic"] = int(round(res_avg["total_traffic"]/len(runs_list)/1000, 0))
    res_avg["alg_proportion"] /= len(runs_list)
    res["average"] = res_avg
    return res

def parse_nb_adversaries(path):
    nb_adv_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for nb_adv in nb_adv_list:
        nb_adv_path = f"{ path }/{ nb_adv }"
        res[nb_adv] = parse_average(nb_adv_path)
    return res

def parse_regions(path):
    regions_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for r in regions_list:
        r_path = f"{ path }/{ r }"
        res[r] = parse_nb_adversaries(r_path)
    return res

def parse_adversaries(path):
    adversaries_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for adv in adversaries_list:
        adv_path = f"{ path }/{ adv }"
        res[adv] = parse_regions(adv_path)
    return res

def parse_algs(path):
    algs_list = [x for x in os.listdir(path) if os.path.isdir(f"{ path }/{ x }")]
    res = dict()
    for alg in algs_list:
        alg_path = f"{ path }/{ alg }"
        res[alg] = parse_adversaries(alg_path)
    return res

def plot_region_on_subplot(ax, x, region, reg_id, data):
    bar = []
    bar_label = []
    bar_width = 0.3
    for nb_adv in sorted([r for r in data]):
        # TODO
        bandwidth_portion = data[nb_adv]["average"]["alg_proportion"]
        bandwidth_total = data[nb_adv]["average"]["total_traffic"]
        bar.append(bandwidth_portion)
        bar_label.append(bandwidth_total)
    rects = ax.bar(x + bar_width*reg_id - (nb_regions-1)*bar_width/2, bar, bar_width, label=region)
    plt.bar_label(rects, bar_label)
    return

def plot_alg_vs_adv(fig, alg_id, alg_name, adv_id, adv_name, data):
    ax = fig.add_subplot(nb_algs, nb_algs, adv_id + alg_id*nb_algs + 1)
    ax.set_title(f"Tested { alg_name } against { adv_name }")
    ax.set_xlabel("Number of adversaries")
    ax.set_ylabel("Fraction of the bandwith")
    ax.set_ylim([0, 1])
    x = np.arange(len(data[list(data.keys())[0]]))
    ax.set_xticks(x, sorted([r for r in data[list(data.keys())[0]]]))
    reg_id = 0
    for region in data:
        plot_region_on_subplot(ax, x, region, reg_id, data[region])
        reg_id += 1
    ax.legend()
    return

def plot_algorithm(fig, alg_id, alg_name, data):
    subplots = []
    adv_id = 0
    for adv in data:
        subplots.append(plot_alg_vs_adv(fig, alg_id, alg_name, adv_id, adv, data[adv]))
        adv_id += 1
    return subplots

def fill_fig(fig, data):
    x = 0
    subplots = []
    for alg in data:
        alg_subplots = plot_algorithm(fig, x, alg, data[alg])
        subplots.extend(alg_subplots)
        x +=1
    return


results = parse_algs(root_results)

nb_regions, nb_algs = len(results[list(results.keys())[0]][list(results.keys())[0]]), len(results)

# print(results)

fig = plt.figure()
fig.set_tight_layout(True)
fig.suptitle('Proportion of bandwidth used by tested subject\n(Total traffic in KB on top of column)', fontsize=16)
fill_fig(fig, results)

plt.show()