import json
import sys
import os

experiment_file = sys.argv[1]
experiment_file_out = sys.argv[2]

if not os.path.isfile(experiment_file):
    print("experiment file not found.")
    exit(1)


with open(experiment_file, 'r') as file:
    experiment_lines = file.read().splitlines()

settings = []
for experiment_line in experiment_lines:
    spawn_locations_str = experiment_line.split('"')[1].replace("'", "").replace("(", "").replace(")", "").split(" ")
    spawn_location_ind = 0
    for spawn_location_str in spawn_locations_str:
        spawn_location_x = int(spawn_location_str.split(";")[0]) - 7
        spawn_location_y = - (int(spawn_location_str.split(";")[1]) - 7)
        set_name = "spawn_location_" + str(spawn_location_ind)
        setting = {"world": "world_" + experiment_line.split(" ")[0] + "_" + experiment_line.split(" ")[1],
                   "group": "entropy_" + experiment_line.split(" ")[1],
                   "set": set_name,
                   "configuration": "-predator_x " + str(spawn_location_x) + " -predator_y " + str(spawn_location_y)}
        settings += [setting]
        spawn_location_ind += 1


with open(experiment_file_out, 'w') as outfile:
    json.dump(settings, outfile)

