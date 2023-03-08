import pickle
from .utils import *
from .model import *
import torch
from torch import optim
import numpy as np
import random
import os
import torch.nn.functional as F
import time
import argparse
from tqdm import tqdm

os.environ["CUDA_VISIBLE_DEVICES"] = "0"

start_time = time.localtime(time.time())
start_time = str(start_time.tm_mon).zfill(2)+str(start_time.tm_mday).zfill(2) + \
    str(start_time.tm_hour).zfill(2)+str(start_time.tm_min).zfill(2)


def train_fnc_cmt_rst(hparams):  # train fnc by reconstruction

    adj, features, struct_assign = load_loc_rst_data(hparams)
    ce_criterion = torch.nn.MSELoss()

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

    g2t_model = GraphAutoencoderTra(hparams).to(hparams.device)
    print(g2t_model)

    model_optimizer = optim.Adam(
        g2t_model.parameters(), lr=hparams.lr)

    for i in tqdm(range(hparams.epochs)):
        # print("epoch", i)
        input_edge, label = generate_edge(adj, hparams.g2t_sample_num)
        label = torch.tensor(label, dtype=torch.float, device=hparams.device)
        input_edge = torch.tensor(
            input_edge, dtype=torch.long, device=hparams.device)
        pred = g2t_model(length_feature, node_feature, adj_tensor, struct_assign, input_edge)
        count = 0

        loss = ce_criterion(pred, label)
        loss.backward(retain_graph=True)
        torch.nn.utils.clip_grad_norm_(
            g2t_model.parameters(), hparams.g2t_clip)
        model_optimizer.step()
        if count % 10 == 0:
            # print(f"loss: {loss.item()}")
            pickle.dump(g2t_model.fnc_assign.tolist(),open(hparams.function_path, "wb"))
            count += 1

    extract_function_assign(hparams)


def train_struct_cmt(hparams):

    adj, features, sp_label = load_gae_data(hparams)

    gae_model = GraphAutoencoder(hparams).to(hparams.device)
    print(gae_model)
    mse_criterion = torch.nn.MSELoss()
    ce_criterion = torch.nn.BCELoss()
    model_optimizer = optim.Adam(gae_model.parameters(), lr=hparams.lr)
    adj_indices = torch.tensor(np.concatenate(
        [adj.row[:, np.newaxis], adj.col[:, np.newaxis]], 1), dtype=torch.long).t()
    adj_values = torch.tensor(adj.data, dtype=torch.float)
    adj_shape = adj.shape
    adj_tensor = torch.sparse.FloatTensor(adj_indices, adj_values, adj_shape)

    length_feature = torch.tensor(
        features[:, 0], dtype=torch.long, device=hparams.device)
    node_feature = torch.tensor(
        features[:, 1], dtype=torch.long, device=hparams.device)
    assign_label = torch.tensor(
        sp_label, dtype=torch.float, device=hparams.device)

    for i in tqdm(range(hparams.epochs)):
        model_optimizer.zero_grad()
        f_edge = gen_false_edge(adj, adj.row.shape[0])
        f_edge = torch.tensor(f_edge, dtype=torch.long, device=hparams.device)
        # print("epoch", i)
        edge_h, struct_adj, pred_cmt_adj, main_assign, edge_e, edge_label = gae_model(
            adj_tensor, length_feature, node_feature, f_edge)
        ce_loss = ce_criterion(edge_e, edge_label)

        loss = ce_criterion(F.softmax(main_assign, 1), assign_label)

        loss.backward(retain_graph=True)
        ce_loss.backward()

        torch.nn.utils.clip_grad_norm_(gae_model.parameters(), 0.1)
        model_optimizer.step()
        # print(f"loss: {ce_loss.item()}")
        if i % 50 == 0:
            pickle.dump(main_assign.tolist(), open(hparams.struct_path, "wb"))

    extract_struct_assign(hparams)

def setup_seed(seed):
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    np.random.seed(seed)
    random.seed(seed)
    torch.backends.cudnn.deterministic = True


def get_newest_file(file_path, file_type):
    dir_list = os.listdir(file_path)
    dir_list = [f for f in dir_list if file_type in f]
    if not dir_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        dir_list = sorted(dir_list,  key=lambda x: os.path.getmtime(os.path.join(file_path, x)))
        # print(dir_list)
        return os.path.join(file_path, dir_list[-1])

if __name__ == '__main__':
    setup_seed(89)

    parser = argparse.ArgumentParser()
    parser.add_argument("--road_num", type=int)
    parser.add_argument("--road_dim", type=int)
    parser.add_argument("--region_num", type=int)
    parser.add_argument("--region_dim", type=int)
    parser.add_argument("--zone_num", type=int)
    parser.add_argument("--zone_dim", type=int)
    parser.add_argument("--epoch", type=int)
    parser.add_argument("--batch_size", type=int)
    parser.add_argument("--lr", type=float)
    parser.add_argument("--dropout", type=float)
    hparams = parser.parse_args()
    hparams = dict_to_object(hparams)

    road_network_path = "../../media/road_network/"
    trajectory_path = "../../media/trajectory/"
    poi_path = "../../media/POI/"

    hparams.road_network = get_newest_file(road_network_path)
    hparams.trajectory = get_newest_file(trajectory_path)
    hparams.poi = get_newest_file(poi_path)
    hparams.alpha = 0.2

    train_struct_cmt(hparams)  # get struct assign by autoencoder

    train_fnc_cmt_rst(hparams)  # get fnc assign by autoencoder -> reconstruct transition graph
