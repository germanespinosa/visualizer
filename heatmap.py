import json
import log_file
import sys
import os
import numpy
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

experiment_name = sys.argv[1]
experiment_path = log_file.results_folder + "/" + experiment_name
img_path = log_file.results_folder + "/" + experiment_name + "/img"


def heatmap(file_name, mat, occlusions, color, spawn_locations):
    fig, ax = plt.subplots()
    fig.set_size_inches(5, 5)
    ax.matshow(mat, cmap=color)
    for ll in ax.get_xticklabels():
        ll.set_visible(False)
    for ll in ax.get_yticklabels():
        ll.set_visible(False)
    for tick in ax.get_xticklines():
        tick.set_visible(False)
    for tick in ax.get_yticklines():
        tick.set_visible(False)
    for x, y in occlusions:
        ax.add_patch(Rectangle((x - .5, 14 - y - .5), width=.95, height=.95, fill=True, color='black', lw=1))
    for x, y in spawn_locations:
        ax.add_patch(Rectangle((x-.5, 14-y-.5), width=.95, height=.95, fill = False, edgecolor='green', lw=3))
    plt.savefig(img_path + "/" + file_name, bbox_inches='tight')
    plt.close(fig)

if not os.path.isdir(img_path):
    os.mkdir(img_path)

experiment = log_file.LoadExperiment(experiment_name)


worlds = {}

for entropyInd in experiment["worlds"].keys():
    entropy = experiment["worlds"][entropyInd]
    worlds[entropyInd] = []
    for simulationInd in entropy.keys():
        simulation = entropy[simulationInd]
        world_name = "world_" + str(simulationInd) + "_" + str(entropyInd)
        worlds[entropyInd] += [{'name': world_name, 'entropy': entropyInd, 'simulation': simulationInd, 'survival_rate': simulation["summary"]["survival_rate"], 'avg_length': simulation["summary"]["avg_length"]}]
        prey_heat_map = numpy.zeros((15, 15))
        prey_success_heat_map = numpy.zeros((15, 15))
        prey_fail_heat_map = numpy.zeros((15, 15))
        predator_heat_map = numpy.zeros((15, 15))
        predator_success_heat_map = numpy.zeros((15, 15))
        predator_fail_heat_map = numpy.zeros((15, 15))
        prey_spawn_locations_heat_maps = [{'all': numpy.zeros((15, 15)), 'success': numpy.zeros((15, 15)), 'fail': numpy.zeros((15, 15))} for x, y in simulation["spawn_locations"]]
        predator_spawn_locations_heat_maps = [{'all': numpy.zeros((15, 15)), 'success': numpy.zeros((15, 15)), 'fail': numpy.zeros((15, 15))} for x, y in simulation["spawn_locations"]]
        episodeInd = 0
        for episode in simulation["result"]["episodes"]:
            episode_result = episode["result"]["result"]
            episode_trajectories = episode["result"]["trajectories"]
            episode_estimated_rewards = episode["result"]["estimated_rewards"]
            spawn_location = (int(episode["predator_start_location"]["x"]), int(episode["predator_start_location"]["y"]))
            prey_spawn_location_heat_map = prey_spawn_locations_heat_maps[simulation["spawn_locations"].index(spawn_location)]
            for position in episode_trajectories[0]:
                prey_heat_map[position["y"] + 7, position["x"] + 7] += 1
                prey_spawn_location_heat_map['all'][position["y"] + 7, position["x"] + 7] += 1
                if episode_result == 1:
                    prey_success_heat_map[position["y"] + 7, position["x"] + 7] += 1
                    prey_spawn_location_heat_map['success'][position["y"] + 7, position["x"] + 7] += 1
                else:
                    prey_fail_heat_map[position["y"] + 7, position["x"] + 7] += 1
                    prey_spawn_location_heat_map['fail'][position["y"] + 7, position["x"] + 7] += 1

            predator_spawn_location_heat_map = predator_spawn_locations_heat_maps[simulation["spawn_locations"].index(spawn_location)]
            for position in episode_trajectories[1]:
                predator_heat_map[position["y"] + 7, position["x"] + 7] += 1
                predator_spawn_location_heat_map['all'][position["y"] + 7, position["x"] + 7] += 1
                if episode_result == 1:
                    predator_success_heat_map[position["y"] + 7, position["x"] + 7] += 1
                    predator_spawn_location_heat_map['success'][position["y"] + 7, position["x"] + 7] += 1
                else:
                    predator_fail_heat_map[position["y"] + 7, position["x"] + 7] += 1
                    predator_spawn_location_heat_map['fail'][position["y"] + 7, position["x"] + 7] += 1
            episodeInd += 1

        heatmap(world_name + "_prey_all", prey_heat_map,
                simulation["occlusions"], 'OrRd', simulation["spawn_locations"])
        heatmap(world_name + "_prey_success", prey_success_heat_map,
                simulation["occlusions"], 'OrRd', simulation["spawn_locations"])
        heatmap(world_name + "_prey_fail", prey_fail_heat_map,
                simulation["occlusions"], 'OrRd', simulation["spawn_locations"])
        heatmap(world_name + "_predator_all", predator_heat_map,
                simulation["occlusions"], 'Blues', simulation["spawn_locations"])
        heatmap(world_name + "_predator_success", predator_success_heat_map,
                simulation["occlusions"], 'Blues', simulation["spawn_locations"])
        heatmap(world_name + "_predator_fail", predator_fail_heat_map,
                simulation["occlusions"], 'Blues', simulation["spawn_locations"])

        for spawn_location in simulation["spawn_locations"]:
            spawn_location_index = simulation["spawn_locations"].index(spawn_location)
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_prey_all_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), prey_spawn_locations_heat_maps[spawn_location_index]["all"],
                     simulation["occlusions"], 'OrRd', [spawn_location])
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_prey_success_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), prey_spawn_locations_heat_maps[spawn_location_index]["success"],
                     simulation["occlusions"], 'OrRd', [spawn_location])
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_prey_fail_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), prey_spawn_locations_heat_maps[spawn_location_index]["fail"],
                     simulation["occlusions"], 'OrRd', [spawn_location])
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_predator_all_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), predator_spawn_locations_heat_maps[spawn_location_index]["all"],
                     simulation["occlusions"], 'Blues', [spawn_location])
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_predator_success_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), predator_spawn_locations_heat_maps[spawn_location_index]["success"],
                     simulation["occlusions"], 'Blues', [spawn_location])
            heatmap("world_" + str(simulationInd) + "_" + str(entropyInd) + "_predator_fail_" + str(spawn_location[0]) + "_" + str(spawn_location[1]), predator_spawn_locations_heat_maps[spawn_location_index]["fail"],
                     simulation["occlusions"], 'Blues', [spawn_location])

with open(experiment_path + '/worlds.json', 'w') as outfile:
    json.dump(worlds, outfile)
