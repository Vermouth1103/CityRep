from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .models import Data, Hyperparameter
from .forms import DataForm, HyperparameterForm

import os
from .model.preprocess.preprocess_roadnetwork import generate_graph, generate_features
from .model.preprocess.preprocess_trajectory import generate_trajectory_adj
from .model.preprocess.preprocess_spectral_cluster import generate_spectral_label
from .model.train import *

def get_newest_file(dir_path, content):
    file_list = os.listdir(dir_path)
    file_list = [f for f in file_list if content in f ]
    if not file_list:
        return
    else:
        # 注意，这里使用lambda表达式，将文件按照最后修改时间顺序升序排列
        # os.path.getmtime() 函数是获取文件最后修改时间
        # os.path.getctime() 函数是获取文件最后创建时间
        file_list = sorted(file_list, key=lambda x: os.path.getmtime(os.path.join(dir_path, x)))
        # print(dir_list)
        return os.path.join(dir_path, file_list[-1])

def handle_uploaded_file(file, data_type):

    root = "media"
    app_name = "representation"

    upload_dir = "upload"
    preprocessed_dir = "preprocessed"

    file_name = file.name
    upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
    absolute_upload_file_path = os.path.join(root, upload_file_path)

    absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
    if not os.path.exists(absolute_upload_dir_path):
        os.makedirs(absolute_upload_dir_path)

    absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir)
    if not os.path.exists(absolute_preprocessed_dir_path):
        os.makedirs(absolute_preprocessed_dir_path)

    with open(absolute_upload_file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # preprocess check
    if data_type == "road_network":
        try:
            adj_matrix, edge_index_dict = generate_graph(absolute_upload_file_path, data_type)

            print(absolute_preprocessed_dir_path)
            road_graph_path = os.path.join(absolute_preprocessed_dir_path, "road_graph.pkl")
            with open(road_graph_path, "wb") as f:
                pickle.dump(adj_matrix, f)
            
            edge_mapping_path = os.path.join(absolute_preprocessed_dir_path, "edge_mapping.json")
            with open(edge_mapping_path, "w") as f:
                json.dump(edge_index_dict, f)

            node_features = generate_features(absolute_upload_file_path, data_type)

            node_features_path = os.path.join(absolute_preprocessed_dir_path, "road_features.pkl")
            with open(node_features_path, "wb") as f:
                pickle.dump(node_features, f)
        except Exception as e:
            print(e)
            return -1
    elif data_type == "trajectory":
        try:
            absolute_road_network_dir_path = os.path.join(root, app_name, upload_dir, "road_network")
            absolute_newest_road_network_path = get_newest_file(absolute_road_network_dir_path, "json")
            tra_adj = generate_trajectory_adj(absolute_upload_file_path, data_type, absolute_newest_road_network_path)

            tra_adj_path = os.path.join(absolute_preprocessed_dir_path, "trajectory_adj.pkl")
            with open(tra_adj_path, "wb") as f:
                pickle.dump(tra_adj, f)
        except Exception as e:
            print(e)
            return -1

    return upload_file_path

# Create your views here.
class RepresentationDesView(View):

    def get(self, request):
        template = "representation/representation_des.html"
        return render(request, template)

class ModelDesView(View):

    def get(self, request):
        template = "representation/model_des.html"
        return render(request, template)

class DataDesView(View):

    def get(self, request):
        template = "representation/data_des.html"
        return render(request, template)

class ModelTrainView(View):

    def get(self, request):
        form = DataForm()
        template = "representation/model_train.html"
        return render(request, template, {"form": form})
    
    def post(self, request):

        form = HyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = Hyperparameter()
            new_hyperparameter.road_num = form.cleaned_data.get("road_num")
            new_hyperparameter.road_dim = form.cleaned_data.get("road_dim")
            new_hyperparameter.region_num = form.cleaned_data.get("region_num")
            new_hyperparameter.region_dim = form.cleaned_data.get("region_dim")
            new_hyperparameter.zone_num = form.cleaned_data.get("zone_num")
            new_hyperparameter.zone_dim = form.cleaned_data.get("zone_dim")
            new_hyperparameter.epochs = form.cleaned_data.get("epochs")
            new_hyperparameter.batch_size = form.cleaned_data.get("batch_size")
            new_hyperparameter.lr = form.cleaned_data.get("lr")
            new_hyperparameter.dropout = form.cleaned_data.get("dropout")
            new_hyperparameter.save()

            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            root = "media"
            app_name = "representation"
            preprocessed_dir = "preprocessed"

            absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir)

            hparams.save_dir = os.path.join(root, app_name, "assign")
            if not os.path.exists(hparams.save_dir):
                os.makedirs(hparams.save_dir)
            hparams.struct_path = os.path.join(hparams.save_dir, "struct_assign.pkl")
            hparams.function_path = os.path.join(hparams.save_dir, "function_assign.pkl")

            hparams.adj = get_newest_file(absolute_preprocessed_dir_path, "graph")
            hparams.node_features = get_newest_file(absolute_preprocessed_dir_path, "features")
            hparams.trajectory = get_newest_file(absolute_preprocessed_dir_path, "trajectory")
            # hparams.poi = get_newest_file(poi_path)
            
            print(f"adj path: {hparams.adj}")
            print(f"node features path: {hparams.node_features}")
            print(f"trajectory path: {hparams.trajectory}")
            hparams.alpha = 0.2
            hparams.length_dim = 32
            hparams.length_num = 2200

            hparams.g2t_sample_num = 2000
            hparams.g2t_clip = 1.0

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

            # spectral clustering
            spectral_label = generate_spectral_label(hparams.adj, hparams.region_num)
            spectral_cluster_path = os.path.join(absolute_preprocessed_dir_path, "spectral_label.pkl")
            with open(spectral_cluster_path, "wb") as f:
                pickle.dump(spectral_label, f)

            hparams.spectral_label = spectral_cluster_path

            train_struct_cmt(hparams)  # get struct assign by autoencoder

            train_fnc_cmt_rst(hparams)  # get fnc assign by autoencoder -> reconstruct transition graph

            return JsonResponse({})
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)
    
class ModelUploadView(View):

    def post(self, request):

        data_type = request.POST.get("type")
        form = DataForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            new_file = Data()
            check = handle_uploaded_file(raw_file, data_type)
            print(f"check: {check}")
            if check == -1:
                data = {"error_msg": f"{data_type} file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = form.cleaned_data.get("type")
                new_file.save()

            data = []
            if data_type == "road_network":
                data.append(check)
            else:
                data.append("")

            files = Data.objects.all().filter(type=data_type).order_by("-id")
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })
            return JsonResponse(data, safe=False)
        else:
            if data_type == "road_network":
                data = {"error_msg": "Only json files are allowed."}
            elif data_type == "trajectory":
                data = {"error_msg": "Only json files are allowed."}
            elif data_type == "POI":
                data = {"error_msg": "Only csv files are allowed."}
            else:
                data = {"error_msg": "Only json, txt, csv files are allowed."}
            return JsonResponse(data)

class ModelPreView(View):

    def get(self, request):
        template = "representation/model_pre.html"
        return render(request, template)