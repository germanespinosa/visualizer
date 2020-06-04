import csv
import json

results_folder = "/home/german/simulation/results"

def LoadOcclusionsFile(file):
    occlusions = []
    with open(file, "r") as file:
        line = file.readline()
        # skip the headers
        line = file.readline()
        while line:
            x = int(line.split(",")[0])
            y = int(line.split(",")[1])
            occlusions += [(x, y)]
            line = file.readline()
    return occlusions

def LoadResultsFile(file):
    with open(file) as f:
        content = f.read()
        content = content.replace("'", '"').replace(",\n]", "\n]")
        return json.loads(content)

def ProcessResults(results):
    summary = {}
    successes = 0
    length = 0
    success_length = 0
    fail_length = 0

    for e in results["episodes"]:
        successes += e["result"]["result"]
        if e["result"]["result"] == 1:
            success_length += e["result"]["lenght"]
        else:
            fail_length += e["result"]["lenght"]
        length += e["result"]["lenght"]

    fails = len(results["episodes"]) - successes
    summary["survival_rate"] = successes / len(results["episodes"])
    summary["avg_length"] = length / len(results["episodes"])

    if successes > 0:
        summary["avg_success_length"] = success_length / successes
    else:
        summary["avg_success_length"] = 0
    if fails > 0:
        summary["avg_fail_length"] = fail_length / fails
    else:
        summary["avg_fail_length"] = 0

    return summary

def ProcessEntropy(entropy):
    summary = {}
    survival_rate = 0
    avg_length = 0
    for k in entropy.keys():
        simulation = entropy[k]
        survival_rate += simulation["summary"]["survival_rate"]
        avg_length += simulation["summary"]["avg_length"]
    summary["survival_rate"] = survival_rate / len(entropy.keys())
    summary["avg_length"] = avg_length / len(entropy.keys())
    return summary


def LoadExperiment(experiment_name):
    folder = results_folder + "/" + experiment_name
    experiment={}
    with open(folder + "/script.sh") as f:
        content = f.read()
    experiment["experiment_file"] = content.split(" ")[1]
    experiment["experiment_name"] = content.split(" ")[2]
    experiment["repetitions"] = content.split(" ")[3]
    experiment["planning_iterations"] = content.split(" ")[4]
    experiment["particles"] = content.split(" ")[5]
    experiment["randomness"] = content.split(" ")[6]
    experiment["predator_path_type"] = content.split(" ")[1]
    experiment["worlds"] = {}
    with open(folder + "/" + experiment["experiment_file"]) as f:
        line = f.readline()
        while line:
            simulation = int(line.split(" ")[0])
            entropy = int(line.split(" ")[1])
            spawn_locations = line.split('"')[1].replace("(", "").replace(")", "").replace("'", "").replace('"', "").split(" ")
            if entropy not in experiment["worlds"].keys():
                experiment["worlds"][entropy] = {}
            experiment["worlds"][entropy][simulation] = {}
            experiment["worlds"][entropy][simulation]["spawn_locations"] = [(int(sl.split(";")[0]), int(sl.split(";")[1])) for sl in spawn_locations]
            occlusions = LoadOcclusionsFile(folder + "/world_" + str(simulation) + "_" + str(entropy) + ".csv")
            experiment["worlds"][entropy][simulation]["occlusions"] = occlusions
            results = LoadResultsFile(folder + "/world_" + str(simulation) + "_" + str(entropy) + ".log")
            experiment["worlds"][entropy][simulation]["result"] = results
            experiment["worlds"][entropy][simulation]["summary"] = ProcessResults(results)
            line = f.readline()
        experiment["summary"] = {}
        for e in experiment["worlds"].keys():
            experiment["summary"][e] = ProcessEntropy(experiment["worlds"][e])
    return experiment
