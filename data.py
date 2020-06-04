import json
import log_file
import sys
import os

experiment_name = sys.argv[1]
experiment_path = log_file.results_folder + "/" + experiment_name

if not os.path.isdir(experiment_name):
    os.mkdir(experiment_name)

experiment = log_file.LoadExperiment(experiment_name)

with open(experiment_path + '/experiment.json', 'w') as outfile:
    json.dump(experiment, outfile)
