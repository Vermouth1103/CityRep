import numpy as np
import json
import pickle
import os

def generate_trajectory_adj(absolute_file_path, _type, road_network_path):
    print(absolute_file_path, _type, road_network_path)
    road_network_path = os.path.join("media", road_network_path)
    print(road_network_path)

    with open(road_network_path, "r") as f:
        road_data = json.load(f)
    
    road_num = len(road_data["features"])
    print(road_num)

    tra_adj = np.zeros((road_num, road_num))

    with open(absolute_file_path, "r") as f:
        tra_dict = json.load(f)

    for tra in tra_dict.values():
        for index in range(len(tra)-1):
            next_index = index + 1
            tra_adj[tra[index]][tra[next_index]] += 1

    print(tra_adj)
    print(np.sum(tra_adj))

    preprocessed_data_path = os.path.join('media', "preprocessed_"+_type, "trajectory_adj.pkl")
    directory = os.path.dirname(preprocessed_data_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(preprocessed_data_path, "wb") as f:
        pickle.dump(tra_adj, f)

if __name__=="__main__":
    pass
    
