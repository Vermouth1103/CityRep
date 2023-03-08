import numpy as np
import json
import pickle
import os

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

if __name__=="__main__":
    pass
    
