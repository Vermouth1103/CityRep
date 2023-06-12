import numpy as np
import json
import pickle
import os

def generate_trajectory_adj(absolute_file_path, data_type, road_network_path):
    with open(road_network_path, "r") as f:
        road_data = json.load(f)
    road_num = len(road_data["features"])
    tra_adj = np.zeros((road_num, road_num))

    with open(absolute_file_path, "r") as f:
        tra_dict = json.load(f)

    for tra in tra_dict.values():
        for index in range(len(tra)-1):
            next_index = index + 1
            tra_adj[tra[index]][tra[next_index]] += 1
    
    return tra_adj

def generate_traj4rp(file_path):

    with open(file_path, "r") as f:
        traj_dict = json.load(f)
    
    route_plan_dataset = list()
    batch_num = 300
    batch_size = 12
    batch_list = list()
    for traj in traj_dict.values():
        if len(batch_list) < batch_size:
            batch_list.append(traj[:8])
        else:
            route_plan_dataset.append(batch_list)
            batch_list = list()
            batch_list.append(traj[:8])
        if len(route_plan_dataset) == batch_num:
            break
    
    return route_plan_dataset

def generate_traj4nlp(file_path):

    with open(file_path, "r") as f:
        traj_dict = json.load(f)
    
    next_loc_dataset = list()
    batch_num = 300
    batch_size = 12
    batch_list = list()
    for traj in traj_dict.values():
        if len(batch_list) < batch_size:
            batch_list.append(traj[:8])
        else:
            next_loc_dataset.append(batch_list)
            batch_list = list()
            batch_list.append(traj[:8])
        if len(next_loc_dataset) == batch_num:
            break
    
    return next_loc_dataset

if __name__=="__main__":
    pass
    
