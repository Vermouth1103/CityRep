from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .models import Data, Hyperparameter
from .forms import DataForm, HyperparameterForm

import os
from .model.preprocess.preprocess_roadnetwork import generate_graph, generate_features
from .model.preprocess.preprocess_trajectory import generate_trajectory_adj, generate_traj4rp
from .model.preprocess.preprocess_spectral_cluster import generate_spectral_label
from .model.train import *

# Create your views here.
def handle_uploaded_file(file, _type, road_network_path=""):

    file_name = file.name
    file_path = os.path.join(_type, file_name)
    absolute_file_path = os.path.join('media', _type, file_name)

    directory = os.path.dirname(absolute_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(absolute_file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)

    # preprocess check
    if _type == "road_network":
        try:
            generate_graph(absolute_file_path, _type)
            generate_features(absolute_file_path, _type)
        except:
            print(e)
            return -1
        
    elif _type == "trajectory":
        try:
            generate_trajectory_adj(absolute_file_path, _type, road_network_path)
        except Exception as e:
            print(e)
            return -1

    return file_path


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
        print(f"POST data: {request.POST}")

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

            road_network_path = "./media/preprocessed_road_network/"
            trajectory_path = "./media/preprocessed_trajectory/"
            # poi_path = "./media/preprocessed_POI/"

            hparams.save_dir = "./media/assign"
            if not os.path.exists(hparams.save_dir):
                os.makedirs(hparams.save_dir)
            hparams.struct_path = os.path.join(hparams.save_dir, "struct_assign.pkl")
            hparams.function_path = os.path.join(hparams.save_dir, "function_assign.pkl")

            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")
            hparams.trajectory = get_newest_file(trajectory_path, "")
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
            spectral_cluster_path = generate_spectral_label(hparams.adj, hparams.region_num)
            hparams.spectral_label = spectral_cluster_path

            train_struct_cmt(hparams)  # get struct assign by autoencoder

            train_fnc_cmt_rst(hparams)  # get fnc assign by autoencoder -> reconstruct transition graph

            template = "poptraffic/poptraffic_downstream_task.html"
            return render(request, template)
        else:
            data = {'error_msg': "Hyper parameter set invalid."}
            return JsonResponse(data)
    
class ModelUploadView(View):

    def post(self, request):
        _type = request.POST.get('type')

        road_network_path = request.POST.get('road_network_path')
        print(f"road_network_path: {road_network_path}")

        form = DataForm(data=request.POST, files=request.FILES)
        print(form.errors)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            new_file = Data()
            check = handle_uploaded_file(raw_file, _type, road_network_path)
            print(check)
            if check == -1:
                data = {"error_msg": _type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = form.cleaned_data.get("type")
                new_file.save()

            data = []
            if _type == "road_network":
                data.append(check)
            else:
                data.append("")

            files = Data.objects.all().filter(type=_type).order_by('-id')
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })
            return JsonResponse(data, safe=False)
        else:
            if _type == "road_network":
                data = {'error_msg': "Only json files are allowed."}
            elif _type == "trajectory":
                data = {'error_msg': "Only json files are allowed."}
            elif _type == "POI":
                data = {'error_msg': "Only csv files are allowed."}
            else:
                data = {'error_msg': "Only json, txt, csv files are allowed."}
            return JsonResponse(data)

class ModelPreView(View):

    def get(self, request):
        template = "representation/model_pre.html"
        return render(request, template)