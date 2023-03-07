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
from tqdm import tqdm

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True

def edit(str1, str2):
    matrix = [[i+j for j in range(len(str2) + 1)] for i in range(len(str1) + 1)]
    for i in range(1,len(str1)+1):
        for j in range(1,len(str2)+1):
            if str1[i-1] == str2[j-1]:
                d = 0
            else:
                d = 1
            matrix[i][j] = min(matrix[i-1][j]+1,matrix[i][j-1]+1,matrix[i-1][j-1]+d)

    return matrix[len(str1)][len(str2)]

def test_route_plan(model, test_loc_set, hparams):
    right = 0
    sum_num = 0
    pred_right = 0
    recall_right = 0
    pred_sum = 0
    recall_sum = 0
    edt_sum = 0
    edt_count = 0
    for batch in test_loc_set:
        batch = np.array(batch)
        if batch.shape[1] < 15:
            continue
        batch = batch[:, :15]
        input_tra = batch[:, :6]
        label = batch[:, 6:-1]
        des = batch[:, -1]
        pred_batch = []
        des = torch.tensor(des, dtype=torch.long, device=hparams.device)
        for step in range(batch.shape[1] - 7):
            input_tra_tensor = torch.tensor(
                input_tra, dtype=torch.long, device=hparams.device)

            pred = model(input_tra_tensor, des)
            pred = pred.view(pred.shape[1], pred.shape[0], pred.shape[2])
            _, pred_loc = torch.topk(pred, 4, dim=2)
            pred_loc = pred_loc.tolist()
            pred_loc = np.array(pred_loc)[:, -1, :]
            pred_batch.append(pred_loc)
            input_tra = np.concatenate(
                (np.array(input_tra.tolist()), pred_loc[:, 0][:, np.newaxis]), 1)
        pred_batch = np.transpose(np.array(pred_batch), (1, 0, 2))
        for tra_pred, tra_label in zip(pred_batch.tolist(), label.tolist()):
            edt_sum += edit([item[0] for item in tra_pred], tra_label)
            edt_count += (len(tra_pred) + len(tra_label)) / 2
            for item in tra_pred:
                for ite in item:
                    if ite in tra_label:
                        pred_right += 1
                        break
            for item in tra_label:
                for cands in tra_pred:
                    if item in cands:
                        recall_right += 1
                        break
            pred_sum += len(tra_pred)
            recall_sum += len(tra_label)
    if edt_count == 0:
        edt_count += 1
    ave_edt = edt_sum / edt_count
    if pred_sum == 0:
        pred_sum += 1
    if recall_sum == 0:
        recall_sum += 1
    print("pred_right:", pred_right, "recall_right:", recall_right,
          "pred_sum:", pred_sum, "recall_sum:", recall_sum)
    precision = float(pred_right) / pred_sum
    recall = float(recall_right) / recall_sum
    f1 = (2 * precision * recall) / (precision + recall + 1e-9)

    print("p/r/f:", precision, recall, f1, "edt:", ave_edt)

def load_model(hparams):

    adj, features, struct_assign, fnc_assign = load_route_plan_data(hparams)

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
    lp_model = RoutePlanModel(hparams, length_feature,
                              node_feature, adj_tensor, struct_assign, fnc_assign).to(hparams.device)

    print(lp_model)

    lp_model.load_state_dict(torch.load("/home/mjt/test/HRNR/beijing/model/route_plan.model"))
    lp_model.eval()
    return lp_model

def train_route_plan(hparams):

    setup_seed(42)

    adj, features, struct_assign, fnc_assign = load_route_plan_data(hparams)
    ce_criterion = torch.nn.CrossEntropyLoss()
    train_loc_set = pickle.load(open(hparams.route_plan_train, "rb"))
    print(len(train_loc_set))
    
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
    
    lp_model = RoutePlanModel(hparams, length_feature,
                              node_feature, adj_tensor, struct_assign, fnc_assign).to(hparams.device)

    model_optimizer = optim.Adam(
        lp_model.parameters(), lr=hparams.lp_learning_rate)

    for i in tqdm(range(hparams.epochs)):
        # print("epoch", i)
        count = 0
        for batch in train_loc_set:
            model_optimizer.zero_grad()
            if len(batch[0]) < 4:
                continue
            input_tra = torch.tensor(
                np.array(batch)[:, :-1], dtype=torch.long, device=hparams.device)
            if len(batch[0]) > 10:
                des = torch.tensor(
                    np.array(batch)[:, 10], dtype=torch.long, device=hparams.device)
            else:
                des = torch.tensor(
                    np.array(batch)[:, -1], dtype=torch.long, device=hparams.device)
                
            pred_label = torch.tensor(
                np.array(batch)[:, 1:], dtype=torch.long, device=hparams.device)
            
            pred = lp_model(input_tra, des)
            
            loss = ce_criterion(
                pred.reshape(-1, hparams.road_num), pred_label.reshape(-1))
            loss.backward(retain_graph=True)
            torch.nn.utils.clip_grad_norm_(
                lp_model.parameters(), hparams.lp_clip)
            model_optimizer.step()
            # if count % 2000 == 0:
            #     print(loss.item())
            count += 1
    torch.save(lp_model.state_dict(), hparams.route_plan_model)

if __name__ == '__main__':
    setup_seed(42)
    parser = argparse.ArgumentParser()
    parser.add_argument("--gpu_id", default=0, type=str, help="gpu id",)
    args = parser.parse_args()
    train_route_plan(args.gpu_id)  # three stage model for loc prediction
