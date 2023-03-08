import json
import pickle
import numpy as np
from sklearn.cluster import SpectralClustering
from scipy import sparse
import os

def generate_spectral_label(road_network_path, region_num, _type="road_network"):
    with open(road_network_path, "rb") as f:
        adj = pickle.load(f)
    
    adj = np.array(adj)
    adj = sparse.coo_matrix(adj)

    sc = SpectralClustering(region_num, affinity='precomputed', n_init=1, assign_labels="discretize")    
    sc.fit(adj)

    spectral_label = []
    for item in sc.labels_:
        a = [0 for i in range(region_num)]
        a[item] = 1
        spectral_label.append(a)
    spectral_label = np.array(spectral_label)

    preprocessed_data_path = os.path.join('media', "preprocessed_"+_type, "spectral_label.pkl")
    directory = os.path.dirname(preprocessed_data_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(preprocessed_data_path, "wb") as f:
        pickle.dump(spectral_label, f)

    return preprocessed_data_path


if __name__=="__main__":
    pass
