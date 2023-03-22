'''
    simple accident simulation 
'''

import pickle
import numpy as np
import math
import networkx as nx
import json

def simulateAccident(embedding, oriSpeed, acciRoadIndex, timeInSecond):
    # embedding: dict{road id: vector}
    # oriSpeed: dict{road id: scaler}
    # acciRoadIndex: scaler
    # timeInSecond: scaler
    # return: dict{road id: scaler}

    roadNum = len(embedding)
    embedKeys, oriSpeedKeys = set(embedding.keys()), set(oriSpeed.keys())

    if roadNum != len(oriSpeed) or roadNum <= 0:
        print('The number of roads is incompatible to the number of speed.')
        raise AssertionError()
    
    print(f"embedKeys: {embedKeys}")
    print(f"oriSpeedKeys: {oriSpeedKeys}")
    if sorted(embedKeys) != sorted(oriSpeedKeys):
        print('Road id is incompatible.')
        raise AssertionError()

    if acciRoadIndex not in embedKeys:
        print('acciRoadIndex is not in embedding.')
        raise AssertionError()

    indexLookup, roadLookup = dict(), dict()
    curRoadList = list(embedding.keys())
    for i in range(roadNum):
        indexLookup[i] = curRoadList[i]
        roadLookup[curRoadList[i]] = i
    
    def wave(oriSpeed, roadEmbed, acciEmbed, t):
        unit = 100.0
        #latUnit = 111195.0;
        #lonUnit = 111195.0*0.67;

        roadEmbed, acciEmbed = np.array(roadEmbed), np.array(acciEmbed)
        r = np.linalg.norm(roadEmbed - acciEmbed) * unit;
        coef = max(min(0.2468*math.cos(0.06*t+1.084) + 0.2415*math.pow(r, 0.1986), 1.0), 0.0);
        print(r, coef)
        curSpeed = oriSpeed * coef;

        return curSpeed

    rtn = dict()
    for i in embedding.keys():
        rtn[i] = wave(oriSpeed[i], embedding[i], embedding[acciRoadIndex], timeInSecond)

    return rtn

def route_plan(G, source_node, target_node):

    if not (source_node in G.nodes() and target_node in G.nodes()):
        print("source node and target node must in G.")
        raise AssertionError()

    if source_node == target_node:
        print("source node and target node are the same.")
        return []
    
    shortest_path = nx.shortest_path(G, source=source_node, target=target_node)
    shortest_path_length = nx.shortest_path_length(G, source=source_node, target=target_node)

    road_map_path = "../data/Road.json"
    road_map = json.load(open(road_map_path, "r"))
    shortest_path_length = 0
    for road in shortest_path:
        shortest_path_length += road_map["features"][road]["properties"]["LENGTH"]
    
    return shortest_path, shortest_path_length


if __name__ == '__main__':
    
    # toy example
    # emb = {3: [2.4592, 1.6893, -3.9873], 10: [3.2323, 0.3431, 5.9870]}
    # speed = {10: 30, 3: 80}
    # index = 3
    # t = 10

    # print(simulateAccident(emb, speed, index, t))

    '''
    # accident influence simulation

    embedding_path = "../output/embedding/road_embedding_fnc"
    embedding = pickle.load(open(embedding_path, "rb"))

    road_mapping_path = "../data/edge_mapping.json"
    road_mapping = json.load(open(road_mapping_path))

    embedding_dict = {}
    for key, value in road_mapping.items():
        embedding_dict[value] = embedding[int(key), :]
    
    speed_dict = {
        road_id_1 : 4,
        road_id_2 : 6,
        ...
    }
    
    accident_road_index = road_id_1

    accident_time = t

    simulateAccident(embedding_dict, speed_dict, accident_road_index, accident_time)
    '''

    '''
    route plan

    graph_path = "../data/graph.pkl"
    graph = pickle.load(open(graph_path, "rb"))
    G = nx.from_numpy_array(graph)

    # print(list(nx.connected_components(G))))
    # print(G)
    # print(G.nodes())
    # # nx.draw(G)
    # # plt.show()

    source_node = 3
    target_node = 10
    shortest_path, shortest_path_length = route_plan(G, source_node, target_node)
    print("shortest path:", shortest_path)
    print("shortest path length:", shortest_path_length)
    '''

    pass