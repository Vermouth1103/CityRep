import subprocess
import os
import sys
import numpy as np
import pandas as pd


def train():
    bigscity_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
    sys.path.append(bigscity_dir)

    result_code = subprocess.call(["python", "run_model.py", '--task', 'traffic_state_pred', '--dataset', 'Xiongan', '--exp_id', '50001'])
    #test = subprocess.run(['ls'])
    

def read_npz(f):
    output_file = pd.DataFrame(columns=['dyna_id', 'id', 'speed'])
    data = np.load(f)
    pre = data['prediction']
    last_pre = pre[-1]

    point_num = pre.shape[2]
    cnt = 0
    id = 0
    for i in range(point_num):
        for j in range(12):
            output_file.loc[cnt] = [int(cnt), int(id), last_pre[j][i][0]]
            cnt += 1
        id += 1
        
    output_file.to_csv('output.csv', index=False)



def predict():
    bigscity_dir = os.path.join(os.path.abspath(os.path.dirname(__file__)), '../')
    sys.path.append(bigscity_dir)
    folder_path = os.path.join(bigscity_dir, 'libcity/cache/50001/evaluate_cache/')

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
        except Exception as e:
            print(f'Error deleting {file_path}: {e}')

    result_code = subprocess.call(["python", "test_model.py", '--task', 'traffic_state_pred', '--dataset', 'Xiongan', '--exp_id', '50001', '--cache_model', './libcity/cache/50001/model_cache/GRU_Xiongan.m'])

    for filename in os.listdir(folder_path):
        if 'npz' in filename:
            read_npz(os.path.join(folder_path, filename))
            break


# train()
predict()