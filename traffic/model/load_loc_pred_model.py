import pickle
from .utils import *
from .loc_model import *
import torch
from torch import optim
import numpy as np
import random
import os
import torch.nn.functional as F
import argparse


def load_model(hparams):

    adj, features, struct_assign, fnc_assign = load_loc_pred_data(
        hparams)

    adj_indices = torch.tensor(np.concatenate(
        [adj.row[:, np.newaxis], adj.col[:, np.newaxis]], 1), dtype=torch.long).t()
    adj_values = torch.tensor(adj.data, dtype=torch.float)
    adj_shape = adj.shape
    adj_tensor = torch.sparse.FloatTensor(adj_indices, adj_values, adj_shape)

    features = features.astype(np.int)

    length_feature = torch.tensor(
        features[:, 0], dtype=torch.long, device=hparams.device)
    node_feature = torch.tensor(
        features[:, 1], dtype=torch.long, device=hparams.device)

    struct_assign = torch.tensor(
        struct_assign, dtype=torch.float, device=hparams.device)
    fnc_assign = torch.tensor(
        fnc_assign, dtype=torch.float, device=hparams.device)

    lp_model = LocPredModel(hparams, length_feature,
                            node_feature, adj_tensor, struct_assign, fnc_assign).to(hparams.device)
    # print('model:', lp_model)

    lp_model.load_state_dict(torch.load(hparams.next_loc_model))
    lp_model.eval()
    return lp_model


def next_loc_pred(hparams):
    
    model = load_model(hparams)
    traj_seq = hparams.traj_seq.split(",")
    traj_seq = np.array([int(road) for road in traj_seq])
    steps = hparams.steps
    for step in range(steps):
        if len(traj_seq.shape) == 1:
            traj_seq = torch.tensor(traj_seq, dtype=torch.long, device=hparams.device).unsqueeze(0)
        else:
            traj_seq = torch.tensor(traj_seq, dtype=torch.long, device=hparams.device)
        # print(traj_seq.shape)
        pred = model(traj_seq)
        pred = pred.view(pred.shape[1], pred.shape[0], pred.shape[2])
        pred_loc = torch.argmax(pred, 2).tolist()
        pred_loc = np.array(pred_loc)[:, -1]

        traj_seq = np.concatenate(
            (np.array(traj_seq.tolist()), pred_loc[:, np.newaxis]), 1)
        print(traj_seq)
    
    return traj_seq.tolist()[0]

def predict(model, steps=1):

    pred_set = load_loc_pred_data(hparams)
    pred_set = torch.tensor(
        pred_set, dtype=torch.long, device=hparams.device)
    for batch in pred_set:
        if len(batch) == 0 or len(batch[0]) < 4:
            continue
        batch = np.array(batch)
        input_tra = batch[:, :-steps]
        for step in range(steps):
            input_tra = torch.tensor(
                input_tra, dtype=torch.long, device=hparams.device)
            pred = model(input_tra)
            pred = pred.view(pred.shape[1], pred.shape[0], pred.shape[2])
            pred_loc = torch.argmax(pred, 2).tolist()
            pred_loc = np.array(pred_loc)[:, -1]

            input_tra = np.concatenate(
                (np.array(input_tra.tolist()), pred_loc[:, np.newaxis]), 1)
        print(input_tra)


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
    hparams = dict_to_object(hparams)

    lp_model = load_model(hparams, args.gpu_id)
    
    predict(lp_model)
