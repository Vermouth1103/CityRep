import numpy as np
import json
import pickle
import os
from sklearn.cluster import SpectralClustering
from scipy import sparse

def generate_graph(absolute_file_path, _type):
    # print(absolute_file_path, _type)
    print(absolute_file_path)
    with open(absolute_file_path, "r") as f:
        road_data = json.load(f)
    roads = road_data["features"]

    source_node_list = []
    end_node_list = []
    edge_index_dict = {}

    road_num = len(roads)
    adj_matrix = np.zeros((road_num, road_num))

    for index, road in enumerate(roads):
        source_node_list.append(road["properties"]["FNODE"])
        end_node_list.append(road["properties"]["TNODE"])
        edge_index_dict[index] = road["properties"]["FID_1"]

    assert len(edge_index_dict) == len(set(list(edge_index_dict.values())))

    source_nodes = np.array(source_node_list)
    end_nodes = np.array(end_node_list)

    for i in range(road_num):
        end_links = np.where(source_nodes==end_nodes[i])[0].tolist()
        source_links = np.where(end_nodes==source_nodes[i])[0].tolist()

        for j in (end_links+source_links): 
            adj_matrix[i][j] = 1

    return adj_matrix, edge_index_dict

def generate_features(absolute_file_path, data_type):
    with open(absolute_file_path, "r") as f:
        road_network = json.load(f)

    features = ["length", "id"]

    node_features = []
    for index, item in enumerate(road_network["features"]):
        node_features.append([item["properties"]["LENGTH"], index])

    node_features = np.array(node_features)
    node_features = node_features.astype(np.int)

    return node_features

if __name__=="__main__":
    path = './media/road_network/1652963341_Road.json'
    _type = 'road_network'
    generate_graph(path, _type)
    generate_features(path, _type)
    
