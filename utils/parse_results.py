import os
import json
import matplotlib.pyplot as plt
import numpy as np

folder_prefix = "auto-"

results = dict() # results[cca][adversary][region][number_of_adversaries][user_id] = transfer_volume


avg = lambda L: sum(L)/len(L)


tcp_ccas = os.listdir("./tests")
tcp_ccas = [x.replace(folder_prefix, "") for x in tcp_ccas if x.startswith(folder_prefix)]
for c in tcp_ccas:
    results[c] = dict()
    other_ccas = os.listdir(f"./tests/{ folder_prefix }{ c }")
    for o_c in other_ccas:
        results[c][o_c] = dict()
        regions = os.listdir(f"./tests/{ folder_prefix }{ c }/{ o_c }")
        for r in regions:
            results[c][o_c][r] = dict()
            adversaries = list(map(int, os.listdir(f"./tests/{ folder_prefix }{ c }/{ o_c }/{ r }")))
            for i in adversaries:
                results[c][o_c][r][i] = dict()
                users = os.listdir(f"./tests/{ folder_prefix }{ c }/{ o_c }/{ r }/{ i }/results/users")
                assert "101.json" in users
                for u in users:
                    u_int = int(u.split("."[0]), 10) - 101
                    content = ""
                    with open(f"./tests/{ folder_prefix }{ c }/{ o_c }/{ r }/{ i }/results/users/{ u }", "r") as f:
                        content = json.loads(f.read())
                        results[c][o_c][r][i][u_int] = dict()
                        results[c][o_c][r][i][u_int]["sent"] = content["end"]["sum_sent"]["bytes"]
                        results[c][o_c][r][i][u_int]["retransmits"] = content["end"]["sum_sent"]["retransmits"]
                results[c][o_c][r][i]["avg_adversary"] = dict()
                results[c][o_c][r][i]["avg_adversary"]["sent"] = avg([results[c][o_c][r][i][j]["sent"] for j in range(1, i+1)])
                results[c][o_c][r][i]["avg_adversary"]["retransmits"] = avg([results[c][o_c][r][i][j]["retransmits"] for j in range(1, i+1)])
                results[c][o_c][r][i]["max_adversary"] = dict()
                results[c][o_c][r][i]["max_adversary"]["sent"] = max([results[c][o_c][r][i][j]["sent"] for j in range(1, i+1)])
                results[c][o_c][r][i]["max_adversary"]["retransmits"] = max([results[c][o_c][r][i][j]["retransmits"] for j in range(1, i+1)])
                results[c][o_c][r][i]["total_adversary"] = dict()
                results[c][o_c][r][i]["total_adversary"]["sent"] = sum([results[c][o_c][r][i][j]["sent"] for j in range(1, i+1)])
                results[c][o_c][r][i]["total_adversary"]["retransmits"] = sum([results[c][o_c][r][i][j]["retransmits"] for j in range(1, i+1)])



# Draw the results

fig = plt.figure()
plot_y = -1
bar_width = 0.3
for cca in results:
    plot_x = 0
    plot_y += 1
    for a_cca in results[cca]:
        ax = fig.add_axes([plot_x, plot_y, 1, 1])
        plot_x += 1
        ax.set_title(f"{ cca } vs { a_cca }")
        ax.set_xlabel("Number of adversaries")
        ax.set_ylabel("Fraction of the bandwith")
        x = None
        reg_id = 0
        for region in results[cca][a_cca]:
            bar = []
            if x == None:
                x = np.arange(len(results[cca][a_cca][region]))
                ax.set_xticks(x, sorted([r for r in results[cca][a_cca][region]]))
            for nb_adv in sorted([r for r in results[cca][a_cca][region]]):
                bandwidth_portion = results[cca][a_cca][region][nb_adv][0]["sent"] / (results[cca][a_cca][region][nb_adv][0]["sent"] + results[cca][a_cca][region][nb_adv]["total_adversaries"]["sent"])
                bar.append(bandwidth_portion)
            rects = ax.bar(x + bar_width*reg_id, bar, bar_width, label=region)
            reg_id += 1
        ax.legend()

plt.show()