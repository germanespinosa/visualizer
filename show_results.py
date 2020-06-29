import json
import sys
import os
import numpy
from scipy.stats import entropy

default_winner = 1
results_folder = "/home/german/simulation/results"

def load_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def save_json(value, filename):
    with open(filename, 'w') as outfile:
        json.dump(value, outfile)

def find_winner(values):
    lv = [v[-1] for v in values]
    episode_winner = default_winner
    for w in range(len(lv)):
        if lv[w] == 100:
            episode_winner = w
    return episode_winner

def find_item_by_name(l,name):
    for i in l:
        if i["name"] == name:
            return True
    return False

def get_item_by_name(l, name):
    for i in l:
        if i["name"] == name:
            return i
    return False


experiment_path = sys.argv[1]
experiment_name = experiment_path.split('/')[-1]
experiment_stats = load_json( experiment_path + "/stats.json")
settings = load_json(experiment_path + "/settings.json")

for g in experiment_stats["groups"]:
    for w in g["worlds"]:
        print(g["name"].replace("plannint_limit_", "") + ", " + str(w["stats"][0]["percent"]) + ", " + str(w["stats"][0]["volatility"][0]) + ", " + str(w["stats"][0]["entropy"]))
