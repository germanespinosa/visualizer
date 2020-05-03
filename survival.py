import sys
import os
import log_file
import numpy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def get_trajectory(ts):
    t = []
    ta = ts.split('/')
    for cs in ta:
        x = int(cs.split(";")[0])
        y = int(cs.split(";")[1])
        t.append((x + 7, y + 7))
    return t

def get_starting_positions(r):
    sps = set()
    for k in r["rows"]:
        x = int(k["starting_position"].split(";")[0].replace("(",""))
        y = int(k["starting_position"].split(";")[1].replace(")",""))
        sps.add((x,y))
    return sps

if len(sys.argv) >= 2:
    if os.path.exists(str(sys.argv[1])):
        print('Source folder:', sys.argv[1])
    else:
        print('Source folder: ', sys.argv[1], "doesn't exists")
        exit(1)
else:
    print('No source folder specified.')
    exit(1)

path_spreads_l = log_file.load("path_spread_UM.csv")
path_spreads = {}
for s in range(len(path_spreads_l["rows"])):
    for e in range(10):
        path_spreads[str(s) + "_" + str(e)] = float(path_spreads_l["rows"][s][str(e)])


survival_rates_l = log_file.load("survival_rates_UM.csv")
survival_rates = {}
for s in range(len(survival_rates_l["rows"])):
    for e in range(10):
        survival_rates[str(s) + "_" + str(e)] = float(survival_rates_l["rows"][s][str(e)])

source_folder = str(sys.argv[1])
results = {}
occlussions = {}
i = 1
starting_positions={}
for r, d, f in os.walk(source_folder):
    for file in f:
        if '.log' in file:
            candidate = file
            if "OcclusionCoordinates" in candidate:
                prefix = candidate.split("_")[0]
                if prefix == "OcclusionCoordinates":
                    prefix = ""
                else:
                    prefix += "_"
                sim=candidate.replace("OcclusionCoordinates_", "").replace(".log", "").replace(prefix, "")
                results[sim] = log_file.load(source_folder + "/" + file)
                starting_positions[sim] = get_starting_positions(results[sim])
                results[sim]["prefix"] = prefix
        if '.csv' in file:
            candidate = file
            if "OcclusionCoordinates" in candidate:
                sim=candidate.replace("OcclusionCoordinates_", "").replace(".csv", "")
                occlussions[sim] = log_file.load(source_folder + "/" + file)


keys = list(results.keys())
keys.sort()

heatmaps = {}
pheatmaps = {}
prefix = ""
row_count = 0
map_size = 15*15
ims = 0
row_count = 0
yaxis=[]
yaxisp=[]
xaxisum=[]
xaxisge=[]
for k in keys:
    fig, my_plots = plt.subplots(ncols=6)
    fig.set_size_inches(40, 7)
    c = 0
    s = 0
    st = numpy.zeros((15, 15))
    ft = numpy.zeros((15, 15))
    tt = numpy.zeros((15, 15))
    spt = numpy.zeros((15, 15))
    fpt = numpy.zeros((15, 15))
    tpt = numpy.zeros((15, 15))
    visited = set()
    pvisited = set()
    for r in results[k]["rows"]:
        trajectory = get_trajectory(r["prey_trajectory"])
        ptrajectory = get_trajectory(r["predator_trajectory"])
        for x, y in trajectory:
            tt[y, x] += 1
        for x, y in ptrajectory:
            tpt[y, x] += 1
        c += 1
        if r["habit_result"] == "1":
            visited.update(trajectory)
            pvisited.update(ptrajectory)
            for x, y in trajectory:
                st[y, x] += 1
            for x, y in ptrajectory:
                spt[y, x] += 1
            s += 1
        else:
            for x, y in trajectory:
                ft[y, x] += 1
            for x, y in ptrajectory:
                fpt[y, x] += 1
    heatmaps[k] = (tt, st, ft)
    pheatmaps[k] = (tpt, spt, fpt)
    ax1, ax2, ax3, pax1, pax2, pax3 = my_plots
    im1 = ax1.matshow(tt, cmap='OrRd')
    ax1.set_title('all')
    im2 = ax2.matshow(st, cmap='OrRd')
    ax2.set_title('successful ' + str(round(s/c*100, 2)) + "% (" + str(round(survival_rates[k]*100,2)) + "%)")
    im3 = ax3.matshow(ft, cmap='OrRd')
    ax3.set_title('fails ' + str(round((c-s)/c*100, 2)) + "%")

    pim1 = pax1.matshow(tpt, cmap='Blues')
    pax1.set_title('all')
    pim2 = pax2.matshow(spt, cmap='Blues')
    pax2.set_title('successful ')
    pim3 = pax3.matshow(fpt, cmap='Blues')
    pax3.set_title('fails ')

    for ax in my_plots:
        for ll in ax.get_xticklabels():
            ll.set_visible(False)
        for ll in ax.get_yticklabels():
            ll.set_visible(False)
        for tick in ax.get_xticklines():
            tick.set_visible(False)
        for tick in ax.get_yticklines():
            tick.set_visible(False)
        for o in occlussions[k]["rows"]:
            ax.add_patch(Rectangle((int(o["X"])-.5, 14-int(o["Y"])-.5), width=.95, height=.95, fill=True, color='black', lw=1))
        for x, y in starting_positions[k]:
            ax.add_patch(Rectangle((x-.5, 14-y-.5), width=.95, height=.95, fill = False, edgecolor='green', lw=3))

    path_spread = round(len(visited) / (map_size - len(occlussions[k])), 2)
    fig.suptitle('Map'+ k + " path spread: " + str(path_spread) + " (" + str(path_spreads[k]) + ")", fontsize=16)
    plt.savefig(source_folder + "/" + results[k]["prefix"] + k, bbox_inches='tight')
    #plt.show()
    plt.close(fig)
    improvement = s/c - survival_rates[k]
    yaxis.append(improvement)
    yaxisp.append(improvement/survival_rates[k]*100)
    xaxisum.append(path_spreads[k])
    xaxisge.append(path_spread)
    ims += improvement
    print(k, " success rate:", s/c, " against", survival_rates[k], " improvement ", round(improvement,4) ," path spread:", path_spread, " against", path_spreads[k])
    row_count += 1

print("average improvement: ", ims/ row_count)

fig, (um, ge) = plt.subplots(ncols=2)
fig.set_size_inches(10, 4)
um.scatter(xaxisum, yaxis)
um.set_title('abs change by path_spread')
um.set_xlabel('path spread MCTS')
um.set_ylabel('improvement')

ge.scatter(xaxisge, yaxis)
ge.set_title('abs change by path_spread')
ge.set_xlabel('path spread Micro-habits')
ge.set_ylabel('improvement')
plt.savefig(source_folder + "/abs_change_path_spread", bbox_inches='tight')
plt.close(fig)

fig, (um, ge) = plt.subplots(ncols=2)
fig.set_size_inches(10, 4)
um.scatter(xaxisum, yaxisp)
um.set_title('% change by path_spread')
um.set_xlabel('path spread MCTS')
um.set_ylabel('improvement')

ge.scatter(xaxisge, yaxisp)
ge.set_title('% change by path_spread')
ge.set_xlabel('path spread Micro-habits')
ge.set_ylabel('improvement')
plt.savefig(source_folder + "/perc_change_path_spread", bbox_inches='tight')
plt.close(fig)
