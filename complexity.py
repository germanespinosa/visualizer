import json
import numpy as np
import random

def load_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def save_json(value, filename):
    with open(filename, 'w') as outfile:
        json.dump(value, outfile)

def get_cell(cells, x,y):
    for cell in cells:
        if cell["coordinates"]["x"] == x and cell["coordinates"]["y"] == y:
            return cell;

def manhattan(s,d):
    return abs(s[0]-d[0]) + abs(s[1]-d[1])

def getStartLocation(info):
    while True:
        x = random.randrange(info["coordinates"][0][0], info["coordinates"][1][0]+1)
        y = random.randrange(info["coordinates"][0][1], info["coordinates"][1][1]+1)
        if manhattan((x, y), (0, 7)) < 7:
            continue
        cell = get_cell(info["world"]["cells"], x, y)
        if cell["occluded"] == 1:
            continue
        return "-predator_x " + str(x) + " -predator_y " + str(y)


info = load_json("worlds_info.json")
info_dic = {}
complexities = []

for i in info:
    if i["complexity"] > 0:
        complexities += [i["complexity"]]
        info_dic[i["world"]["name"]] = i

hist, bin_edges = np.histogram(complexities)
print(bin_edges)
print(hist)

bins = {}
for i in info:
    for e in range(len(bin_edges)-1):
        if bin_edges[e] < i["complexity"] < bin_edges[e+1]:
            key = "from_" + str(round(bin_edges[e],2)) + "_to_" + str(round(bin_edges[e + 1],2))
            if key not in bins.keys():
                bins[key] = [i["world"]["name"]]
            else:
                bins[key] += [i["world"]["name"]]


groups = {}
for key in bins.keys():
    bin = bins[key]
    if len(bin) >= 10:
        random.shuffle(bin)
        groups[key] = bin[0:10]

settings=[];
for key in groups.keys():
    for world in groups[key]:
        for pred_location in range(10):
            settings += [{"group": key, "world": world, "set": "spawn_location_"+str(pred_location), "configuration": getStartLocation(info_dic[world])}]

print(settings)

save_json(settings, "complexity.json")

planning_limits = [0, 100, 500, 1000, 5000, 10000, 15000, 20000, 30000, 50000, 100000, 150000, 200000, 300000, 500000]
for key in groups.keys():
    settings = []
    for world in groups[key]:
        for pred_location in range(10):
            pred_location_x_y = getStartLocation(info_dic[world])
            for planning_limit in planning_limits:
                settings += [{"group": "plannint_limit_" + str(planning_limit), "world": world, "set": "spawn_location_"+str(pred_location), "configuration": pred_location_x_y + " -planning_limit "+str(planning_limit)}]
    save_json(settings, "complexity_" + key + ".json")




