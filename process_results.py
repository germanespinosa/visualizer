import json
import sys
import os
import numpy

default_winner = 1
results_folder = "/home/german/simulation/results"

def generate_heat_map_img(file_prefix, dataset, occlusions, stats):
    heat_map_data = dataset["heat_map"]
    spawn_locations = heat_map_data["spawn_locations"]
    spawn_locations_lists = []
    for agent_spawn_locations_ind in range(len(spawn_locations)):
        positions = spawn_locations[agent_spawn_locations_ind]
        spawn_locations_list = []
        for position in positions:
            x, y = to_map_coordinates(position, heat_map_data["coordinates"])
            spawn_locations_list += [[x, y]]
        spawn_locations_lists += [spawn_locations_list]

    occlusions_list = []
    for position in occlusions:
        x, y = to_map_coordinates(position, heat_map_data["coordinates"])
        occlusions_list.append([x, y])

    path_diversities = []
    for agent_ind in range(len(heat_map_data["data"])):
        agent_data = heat_map_data["data"][agent_ind]
        for result_ind in range(len(agent_data)):
            data = agent_data[result_ind]
            if agent_ind==0:
                path_diversities += [data.copy()]
            else:
                path_diversities[result_ind] += data
            path_diversity = float(numpy.count_nonzero(data)) / float(data.size-len(occlusions))
            stats[result_ind]["path_diversity"][agent_ind] = path_diversity
            file_name = dataset["name"] + "_" + str(result_ind) + "_" + str(agent_ind)
            heat_map_info = {"cells": data.tolist(),
                             "occlusions": occlusions_list,
                             "coordinates": heat_map_data["coordinates"],
                             "spawn_locations": spawn_locations_lists}
            save_json(heat_map_info, file_prefix + file_name + ".json")
    for result_ind in range(len(path_diversities)):
        path_diversity = float(numpy.count_nonzero(path_diversities[result_ind])) / float(path_diversities[result_ind].size - len(occlusions))
        stats[result_ind]["path_diversity"][-1] = path_diversity

def create_heat_map_data(agent_count, possible_results_count, map_coordinates):
    dimensions = (map_coordinates[1][0] - map_coordinates[0][0] + 1, map_coordinates[1][1] - map_coordinates[0][1] + 1)
    values = {"coordinates": map_coordinates, "spawn_locations": [], "dimensions": dimensions, "data": []}
    for agent_ind in range(agent_count):
        data = []
        for pr in range(possible_results_count):
            data += [numpy.zeros(dimensions, dtype=int)]
        data += [numpy.zeros(dimensions, dtype=int)]
        values["data"] += [data]
        values["spawn_locations"] += [[]]
    return values


def accumulate_heat_map_data(destination, source):
    for agent_ind in range(len(destination["data"])):
        for result_ind in range(len(destination["data"][agent_ind])):
            destination["data"][agent_ind][result_ind] += source["data"][agent_ind][result_ind]
        sl = set()
        sl.update(destination["spawn_locations"][agent_ind])
        sl.update(source["spawn_locations"][agent_ind])
        destination["spawn_locations"][agent_ind] = list(sl)

def to_map_coordinates(position, world_coordinates):
    return position[0]-world_coordinates[0][0], (position[1])-world_coordinates[0][1]


def add_trajectories(data, trajectories, winner):
    heat_map_data = data["heat_map"]

    agent_count = len(trajectories)
    size = heat_map_data["dimensions"][0] * heat_map_data["dimensions"][1]
    data = {"length": [0] * agent_count,
            "distance": [0] * agent_count,
            "path_diversity": [0] * agent_count,
            "cell_revisit": [0] * agent_count,
            "complexity": data["complexity"],
            "winner": winner}
    for trajectory_ind in range(agent_count):
        unique = set()
        trajectory_data = heat_map_data["data"][trajectory_ind]
        first = True
        px, py = to_map_coordinates( trajectories[trajectory_ind][0], heat_map_data["coordinates"])
        for position in trajectories[trajectory_ind]:
            x, y = to_map_coordinates(position, heat_map_data["coordinates"])
            data["distance"][trajectory_ind] += abs(x-px) + abs(y-py)
            px, py = x, y
            if first:
                heat_map_data["spawn_locations"][trajectory_ind] += [tuple(position)]
                first = False
            trajectory_data[-1][y, x] += 1
            trajectory_data[winner][y, x] += 1
            unique.add((x, y))
        cells_visited = len(unique)
        data["length"][trajectory_ind] = len(trajectories[trajectory_ind])
        data["cell_revisit"][trajectory_ind] = len(trajectories[trajectory_ind]) - cells_visited
        data["path_diversity"][trajectory_ind] = 0
    return data


def create_data_point(agent_count):
    return


def create_stats(agent_count):
    return [{
                "count": 0,
                "percent": 0.0,
                "length": [0] * (agent_count+1),
                "distance": [0] * (agent_count+1),
                "path_diversity": [0] * (agent_count+1),
                "cell_revisit": [0] * (agent_count+1),
                "complexity": 0
            } for x in range(agent_count + 1)]


def load_json(filename):
    with open(filename) as f:
        return json.loads(f.read())


def save_json(value, filename):
    with open(filename, 'w') as outfile:
        json.dump(value, outfile)


def weighted_avg(count, value, data_point):
    return (float(count) * float(value) + float(data_point)) / (float(count) + 1.0)


def update_stats(info, data):
    stats = info["stats"]
    agent_count = len(stats)-1
    episode_winner = data["winner"]

    winner_stats = stats[episode_winner]
    all_stats = stats[-1]

    for k in winner_stats.keys():
        if k != "count" and k != "percent":
            if type(data[k]) is list:
                for agent_ind in range(agent_count):
                    winner_stats[k][agent_ind] = weighted_avg(winner_stats["count"],
                                                              winner_stats[k][agent_ind],
                                                              data[k][agent_ind])
                    all_stats[k][agent_ind] = weighted_avg(all_stats["count"],
                                                           all_stats[k][agent_ind],
                                                           data[k][agent_ind])
                for agent_ind in range(agent_count):
                    winner_stats[k][agent_count] = weighted_avg(agent_ind,
                                                                winner_stats[k][agent_count],
                                                                winner_stats[k][agent_ind])
                    all_stats[k][agent_count] = weighted_avg(agent_ind,
                                                             all_stats[k][agent_count],
                                                             all_stats[k][agent_ind])
            else:
                winner_stats[k] = weighted_avg(winner_stats["count"],
                                               winner_stats[k],
                                               data[k])
                all_stats[k] = weighted_avg(all_stats["count"],
                                            all_stats[k],
                                            data[k])

    winner_stats["count"] += 1
    all_stats["count"] += 1
    for i in range(len(stats)-1):
        stats[i]["percent"] = float(stats[i]["count"]) * 100.0 / float(all_stats["count"])
    all_stats["percent"] = 100


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
agents_names = ["prey", "predator"]
colors_set = ["Reds", "Blues"]
experiment_stats = {"name": experiment_name, "stats": create_stats(len(agents_names)), "groups": []}
settings = load_json(experiment_path + "/settings.json")
experiment_data = load_json(experiment_path + "/experiment.json")
map_dimensions = (15, 15)

groups = []
groups_names = []
for setting in settings:

    if not find_item_by_name(groups, setting["group"]):
        groups_names += [setting["group"]]
        groups += [{"name": setting["group"],
                    "worlds": []}]
        experiment_stats["groups"] += [{"name": setting["group"],
                                        "stats": create_stats(len(agents_names)),
                                        "worlds": []}]
    group = get_item_by_name(groups, setting["group"])
    group_stats = get_item_by_name(experiment_stats["groups"], setting["group"])

    if not find_item_by_name(group["worlds"], setting["world"]):
        world_info = load_json(experiment_path + "/" + setting["group"] + "/" +
                               setting["world"] + "/world.json")
        world_info.update({"name": setting["world"],
                           "heat_map": create_heat_map_data(2, 2, world_info["coordinates"]),
                           "sets": [],
                           "complexity": world_info["complexity"]})
        group["worlds"] += [world_info]
        group_stats["worlds"] += [{"name": setting["world"],
                                   "stats": create_stats(len(agents_names)),
                                   "sets": []}]

    world = get_item_by_name(group["worlds"], setting["world"])
    world_stats = get_item_by_name(group_stats["worlds"], setting["world"])

    if not find_item_by_name(world["sets"], setting["set"]):
        world["sets"] += [{"name": setting["set"],
                           "stats": create_stats(len(agents_names)),
                           "heat_map": create_heat_map_data(2, 2, world["coordinates"]),
                           "episodes": [],
                           "complexity": world["complexity"]}]
        world_stats["sets"] += [{"name": setting["set"],
                                 "stats": create_stats(len(agents_names)),
                                 "episodes": []}]

    set_ = get_item_by_name(world["sets"], setting["set"])
    set_stats = get_item_by_name(world_stats["sets"], setting["set"])

    episodes = load_json(experiment_path + "/" + setting["group"] + "/" +
                         setting["world"] + "/" + setting["set"] + "/episodes.json")

    for episode in episodes:
        winner = find_winner(episode["values"])
        episode_data = add_trajectories(set_, episode["trajectories"], winner)
        set_stats["episodes"].append(episode_data)
        update_stats(set_stats, episode_data)
        update_stats(world_stats, episode_data)
        update_stats(group_stats, episode_data)
        update_stats(experiment_stats, episode_data)


img_path = experiment_path + "/heatmaps"

save_json(groups_names, experiment_path + "/results.json")

if not os.path.isdir(img_path):
    os.mkdir(img_path)

for group in groups:
    group_name = group["name"]
    group_stats = get_item_by_name(experiment_stats["groups"],group_name)
    if not os.path.isdir(img_path + "/" + group_name):
        os.mkdir(img_path + "/" + group["name"])
    for world in group["worlds"]:
        world_name = world["name"]
        world_stats = get_item_by_name(group_stats["worlds"], world_name)
        if not os.path.isdir(img_path + "/" + group_name + "/" + world_name):
            os.mkdir(img_path + "/" + group_name + "/" + world_name)
        for set_ in world["sets"]:
            set_name = set_["name"]
            set_stats = get_item_by_name(world_stats["sets"],set_name)
            accumulate_heat_map_data(world["heat_map"], set_["heat_map"])
            generate_heat_map_img(img_path + "/" + group_name + "/" + world_name + "/",
                                                   set_,
                                                   world["occlusions"], set_stats["stats"])

        generate_heat_map_img(img_path + "/" + group_name + "/",
                                               world,
                                               world["occlusions"], world_stats["stats"])
        for result_ind in range(len(group_stats["stats"])):
            for agent_ind in range(len(group_stats["stats"][result_ind]["path_diversity"])):
                group_stats["stats"][result_ind]["path_diversity"][agent_ind] += world_stats["stats"][result_ind]["path_diversity"][agent_ind]
    for result_ind in range(len(group_stats["stats"])):
        for agent_ind in range(len(group_stats["stats"][result_ind]["path_diversity"])):
            group_stats["stats"][result_ind]["path_diversity"][agent_ind] /= len(group["worlds"])


save_json(experiment_stats, experiment_path + "/stats.json")


if os.path.exists(results_folder + "/experiments.json"):
    experiments = load_json(results_folder + "/experiments.json")
else:
    experiments = []

found = False
for experiment in experiments:
    if experiment["experiment_name"] == experiment_name:
        found = True

if not found:
    experiments += [experiment_data]
    save_json(experiments, results_folder + "/experiments.json")
