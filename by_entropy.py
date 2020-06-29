import json
import sys
import random
import matplotlib

results_folder = "/home/german/simulation/results"

def load_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def save_json(value, filename):
    with open(filename, 'w') as outfile:
        json.dump(value, outfile)

experiments = ["complexity_from_4.31_to_4.66",
               "complexity_from_4.66_to_5.0",
               "complexity_from_5.0_to_5.35",
               "complexity_from_5.35_to_5.69",
               "complexity_from_5.69_to_6.03",
               "complexity_from_6.03_to_6.38" ]

planning_limits = [0, 100, 500, 1000, 5000, 10000, 15000, 20000, 30000, 50000, 100000, 150000, 200000, 300000, 500000]

for entropy_bucket in range(11):
    selected_worlds = set()
    for experiment in experiments:
        experiment_path = results_folder + "/" + experiment
        experiment_stats = load_json( experiment_path + "/stats.json")
        for g in experiment_stats["groups"]:
            for w in g["worlds"]:
                eb = round(w["stats"][0]["entropy"] * 10)
                if eb == entropy_bucket:
                    selected_worlds.update([w["name"]]);

    new_settings = []
    for world_name in selected_worlds:
        for experiment in experiments:
            experiment_path = results_folder + "/" + experiment
            settings = load_json(experiment_path + "/settings.json")
            for setting in settings:
                if setting["world"] == world_name:
                    setting["group"] = setting["group"].replace("plannint_limit_", "")
                    new_settings += [setting]

    save_json(new_settings, "entropy_bucket_" + str(entropy_bucket) + ".json")
