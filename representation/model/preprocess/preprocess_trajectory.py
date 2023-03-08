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

if __name__=="__main__":
    pass
    
