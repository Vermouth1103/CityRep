import pickle
from .utils import *
from .route_model import *
import torch
from torch import optim
import numpy as np
import random
import os
import torch.nn.functional as F
import argparse
import networkx as nx

def load_model(hparams):
    
    adj, features, struct_assign, fnc_assign = load_route_plan_data(hparams)

    adj_indices = torch.tensor(np.concatenate(
        [adj.row[:, np.newaxis], adj.col[:, np.newaxis]], 1), dtype=torch.long).t()
    adj_values = torch.tensor(adj.data, dtype=torch.float)
    adj_shape = adj.shape
    adj_tensor = torch.sparse.FloatTensor(adj_indices, adj_values, adj_shape)

    features = features.astype(int)

    length_feature = torch.tensor(
        features[:, 0], dtype=torch.long, device=hparams.device)
    node_feature = torch.tensor(
        features[:, 1], dtype=torch.long, device=hparams.device)

    struct_assign = torch.tensor(
        struct_assign, dtype=torch.float, device=hparams.device)
    fnc_assign = torch.tensor(
        fnc_assign, dtype=torch.float, device=hparams.device)
    lp_model = RoutePlanModel(hparams, length_feature,
                            node_feature, adj_tensor, struct_assign, fnc_assign).to(hparams.device)

    print('model:', lp_model)

    lp_model.load_state_dict(torch.load(hparams.route_plan_model))
    lp_model.eval()
    return lp_model

def route_plan_pred(hparams):
    
    # model = load_model(hparams)
    adj = pickle.load(open(hparams.adj, "rb"))
    G = nx.from_numpy_matrix(adj)

    shortest_path = nx.shortest_path(G, source=int(hparams.start), target=int(hparams.end))
    print(shortest_path)
    return shortest_path

def predict(model, steps=1):

    pred_set = get_route_plan_data(hparams)
    output = []
    for batch in pred_set:
        batch = np.array(batch)
        if batch.shape[1] < 7:
            continue
        # batch = batch[:, :15]
        input_tra = batch[:, :6]
        des = batch[:, -1]
        pred_batch = []
        des = torch.tensor(des, dtype=torch.long, device=hparams.device)
        for step in range(batch.shape[1] - 7):
            input_tra_tensor = torch.tensor(
                input_tra, dtype=torch.long, device=hparams.device)
            pred = model(input_tra_tensor, des)
            # print(pred.shape)
            pred = pred.view(pred.shape[1], pred.shape[0], pred.shape[2])
            _, pred_loc = torch.topk(pred, 4, dim=2)
            pred_loc = pred_loc.tolist()
            # print(pred_loc)
            pred_loc = np.array(pred_loc)[:, -1, :]
            # print(pred_loc)
            pred_batch.append(pred_loc)
            input_tra = np.concatenate(
                (np.array(input_tra.tolist()), pred_loc[:, 0][:, np.newaxis]), 1)
            # print(input_tra)
        pred_batch = np.transpose(np.array(pred_batch), (1, 0, 2))

        output.append(np.squeeze(pred_batch[:, :, 0]).tolist())
    print(output)


def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


if __name__ == '__main__':
    setup_seed(89)
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu_id", default=0, type=str, help="gpu id")
    args = parser.parse_args()
    hparams = dict_to_object(beijing_route_hparams)

    lp_model = load_model(hparams, args.gpu_id)
    
    predict(lp_model)
