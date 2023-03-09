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

def test_loc_pred(model, test_loc_set, hparams, steps):
    right = 0
    sum_num = 0
    right_5 = 0
    count = 0
    # print(len(test_loc_set))
    for batch in test_loc_set:
        if len(batch) == 0 or len(batch[0]) < 4:
            continue
        # print("count", count)  
        count += 1
        batch = np.array(batch)
        input_tra = batch[:, :-steps]
        label = batch[:, -1]
        for step in range(steps):
            input_tra = torch.tensor(input_tra, dtype=torch.long, device = hparams.device)  
            label_tensor = torch.tensor(label, dtype=torch.long, device = hparams.device)  

            pred = model(input_tra)    
            pred = pred.view(pred.shape[1], pred.shape[0], pred.shape[2])
            pred_loc = torch.argmax(pred, 2).tolist()
            pred_loc = np.array(pred_loc)[:, -1]
            # print(pred.shape)
            pred_5 = (-np.array(pred.tolist())).argsort()[:, :, :5]
            
            input_tra = np.concatenate((np.array(input_tra.tolist()), pred_loc[:, np.newaxis]), 1)
            # print("pred_5:", pred_5)  
        for item1, item2, item3 in zip(pred_loc.tolist(), label.tolist(), pred_5[:, -1, :].tolist()):
            if item1 == item2:
                right += 1
            if item2 in item3:
                right_5 += 1    
            sum_num += 1

    print("prediction @acc:", float(right)/sum_num)      
    print("prediction @acc5", float(right_5)/sum_num)

def train_loc_pred(hparams):

    setup_seed(89)

    adj, features, struct_assign, fnc_assign = load_loc_pred_data(hparams) 
    ce_criterion = torch.nn.CrossEntropyLoss()

    # test_loc_set = pickle.load(open("data/loc_test_set", "rb"))
    train_loc_set = pickle.load(open(hparams.next_loc_train, "rb"))
    print(len(train_loc_set))

    adj_indices = torch.tensor(np.concatenate([adj.row[:, np.newaxis], adj.col[:, np.newaxis]], 1), dtype=torch.long).t()
    adj_values = torch.tensor(adj.data, dtype=torch.float)
    adj_shape = adj.shape
    adj_tensor = torch.sparse.FloatTensor(adj_indices, adj_values, adj_shape)

    features = features.astype(int)

    length_feature = torch.tensor(features[:, 0], dtype=torch.long, device = hparams.device)
    node_feature = torch.tensor(features[:, 1], dtype=torch.long, device = hparams.device)

    struct_assign = torch.tensor(struct_assign, dtype=torch.float, device = hparams.device)
    fnc_assign = torch.tensor(fnc_assign, dtype=torch.float, device = hparams.device)

    lp_model = LocPredModel(hparams, length_feature, node_feature, adj_tensor, struct_assign, fnc_assign).to(hparams.device)

    model_optimizer = optim.Adam(lp_model.parameters(), lr=hparams.lp_learning_rate)
    print('lp_model:', lp_model)

    for i in tqdm(range(hparams.epochs)):
        # print("epoch", i)
        count = 0
        for batch in train_loc_set:
            # print('batch:', batch)
            model_optimizer.zero_grad()  
            if len(batch[0]) < 4: 
                continue     
            input_tra = torch.tensor(np.array(batch)[:, :-1], dtype=torch.long, device = hparams.device)  
            pred_label = torch.tensor(np.array(batch)[:, 1:], dtype=torch.long, device = hparams.device)  

            pred = lp_model(input_tra)
            # pred = pred.permute(1, 0, 2)
            loss = ce_criterion(pred.reshape(-1, hparams.road_num), pred_label.reshape(-1))
            loss.backward()
            torch.nn.utils.clip_grad_norm_(lp_model.parameters(), hparams.lp_clip)
            model_optimizer.step()
            # if count % 2000 == 0:
            #     test_loc_pred(lp_model, test_loc_set, hparams, 1)  
            count += 1
            # test_loc_pred(lp_model, test_loc_set, hparams, 1)  
            # test_loc_pred(lp_model, test_loc_set, hparams, 5)  
            # print("step ", str(count))
            # print(loss.item())
    torch.save(lp_model.state_dict(), hparams.next_loc_model)

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
    train_loc_pred(args.gpu_id)  # three stage model for loc prediction
