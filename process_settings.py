import json
import sys
import os
import numpy

def load_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def save_json(value, filename):
    with open(filename, 'w') as outfile:
        json.dump(value, outfile)


experiment_settings = load_json(sys.argv[1])
experiment_parameters = experiment_settings["parameters"]
for group in experiment_settings["groups"]:
    group_settings = experiment_settings.copy()
    group_settings.update(group["parameters"])
    for world in group["worlds"]:
        world_settings = group_settings.copy()
        world_settings.update(world["[parameters"])
        for set_ in world["sets"]:
            set_settings = world_settings.copy()
            set_settings.update(set_["parameters"])
            for key in set_settings.keys():
                print("-" + key, set_settings[key], sep=" ", end=" ")
            print()

