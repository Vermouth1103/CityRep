import pickle
import numpy as np
from scipy import sparse
import random
import copy
from sklearn.utils import shuffle
import json

EPS = 1e-30


def gen_false_edge(adj, num):
    #  adj = copy.deepcopy(adj)
    adj = adj.todense()
    edges = []
    while len(edges) < num:
        start = random.randint(0, len(adj) - 1)
        end = random.randint(0, len(adj) - 1)
        if adj[start, end] == 0 and adj[end, start] == 0:
            edges.append([start, end])
    edges = np.array(edges)
    edges = edges.transpose()
    return edges


def generate_edge(adj, num):  # generate edge to train g2t model
    false_edges = gen_false_edge(adj, num / 2)
    false_edges = false_edges.transpose().tolist()
    true_edges = []
    t_labels = []
    while len(true_edges) < num / 2:
        ind = random.randint(0, len(adj.data) - 1)
        start = adj.row[ind]
        end = adj.col[ind]
        true_edges.append([start, end])
        t_labels.append(adj.data[ind])
    edges = false_edges
    edges.extend(true_edges)

    edges = np.array(edges)
    edges = edges.transpose()
    f_labels = [0.0 for i in range(1000)]
    labels = []
    labels.extend(f_labels)
    labels.extend(t_labels)

    return edges, labels


def load_loc_rst_data(hparams):

    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)

    node_features = pickle.load(open(hparams.node_features, "rb"))

    spectral_label = pickle.load(open(hparams.spectral_label, "rb"))

    return adj, node_features, spectral_label

def load_g2s_data(hparams):
    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)
    node_features = pickle.load(open(hparams.node_features, "rb"))
    node_features = node_features.tolist()
    while len(node_features) < 16000:
        node_features.append(['0', '0', '0', '0'])
    node_features = np.array(node_features)

    spectral_label = pickle.load(open(hparams.spectral_label, "rb"))
    train_cmt_set = pickle.load(open(hparams.train_cmt_set, "rb"))

    return adj, node_features, spectral_label, train_cmt_set



def load_g2s_loc_data(hparams):
    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)
    node_features = pickle.load(open(hparams.node_features, "rb"))
    node_features = node_features.tolist()
    while len(node_features) < 16000:
        node_features.append(['0', '0', '0', '0'])
    node_features = np.array(node_features)

    spectral_label = pickle.load(open(hparams.spectral_label, "rb"))
    train_loc_set = pickle.load(open(hparams.train_loc_set, "rb"))

    return adj, node_features, spectral_label, train_loc_set


def load_gae_data(hparams):
    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)
    node_features = pickle.load(open(hparams.node_features, "rb"))

    spectral_label = pickle.load(open(hparams.spectral_label, "rb"))

    return adj, node_features, spectral_label

def load_route_plan_data(hparams):
    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)
    node_features = pickle.load(open(hparams.node_features, "rb"))

    struct_assign = pickle.load(open(hparams.struct_path, "rb"))
    fnc_assign = pickle.load(open(hparams.function_path, "rb"))

    return adj, node_features, struct_assign, fnc_assign

def load_data(hparams):

    train_loc_set = pickle.load(open(hparams.train_loc_set, "rb"))
    train_time_set = pickle.load(open(hparams.train_time_set, "rb"))
    adj = pickle.load(open(hparams.adj, "rb"))
    self_loop = np.eye(len(adj))
    adj = np.array(adj) + self_loop
    adj = sparse.coo_matrix(adj)
    test_loc_set = train_loc_set[6000:]
    test_time_set = train_time_set[6000:]
    train_loc_set = train_loc_set[:6000]
    train_time_set = train_time_set[:6000]
    return train_loc_set, train_time_set, adj, test_loc_set, test_time_set


class Dict(dict):
    __setattr__ = dict.__setitem__
    __getattr__ = dict.__getitem__


def dict_to_object(dictObj):
    if not isinstance(dictObj, dict):
        return dictObj
    inst = Dict()
    for k, v in dictObj.items():
        inst[k] = dict_to_object(v)
    return inst


def get_route_plan_data(hparams):
    route_plan_data = pickle.load(open(hparams.route_predict_set, "rb"))
    return route_plan_data


def extract_struct_assign(hparams):
    with open(hparams.struct_path, "rb") as f:
        struct_assign = np.array(pickle.load(f))

    assign_list = np.argmax(struct_assign, axis=1)
    print(f"struct assign list: {assign_list}, number: {len(assign_list)}")

    assign_dict = {}
    for index, value in enumerate(assign_list):
        if int(value) not in assign_dict:
            assign_dict[int(value)] = [int(index)]
        else:
            assign_dict[int(value)].append(int(index))
    print(f"struct assign dict: {assign_dict}, number:  {len(assign_dict)}")

    with open("./media/assign/struct_assign.json", "w") as f:
        json.dump(assign_dict, f)

def extract_function_assign(hparams):
    with open(hparams.struct_path, "rb") as f:
        struct_assign = np.array(pickle.load(f))
    with open(hparams.function_path, "rb") as f:
        function_assign = np.array(pickle.load(f))

    node2fnc = np.dot(struct_assign, function_assign)
    print(f"node2fnc: {node2fnc}, {node2fnc.shape}")

    assign_list = np.argmax(node2fnc, axis=1)
    print(f"function assign list: {assign_list}, number: {len(assign_list)}")

    assign_dict = {}
    for index, value in enumerate(assign_list):
        if int(value) not in assign_dict:
            assign_dict[int(value)] = [int(index)]
        else:
            assign_dict[int(value)].append(int(index))
    print(f"function assign dict: {assign_dict}, number:  {len(assign_dict)}")

    with open("./media/assign/struct_fnc.json", "w") as f:
        json.dump(assign_dict, f)