from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from django.contrib.auth.mixins import LoginRequiredMixin

from .models import RepresentationData, RepresentationHyperparameter, AccidentData, RoutePlanData, RoutePlanHyperparameter, NextLocData, NextLocHyperparameter, SpeedPredictionData
from .forms import RepresentationDataForm, RepresentationHyperparameterForm, AccidentDataForm, AccidentPredForm, RoutePlanDataForm, RoutePlanHyperparameterForm, RoutePlanPredForm, NextLocDataForm, NextLocHyperparameterForm, NextLocPredForm, SpeedPredictionDataForm, SpeedPredictionPredForm

import os
import pandas as pd
import numpy
from .model.preprocess.preprocess_roadnetwork import generate_graph, generate_features
from .model.preprocess.preprocess_trajectory import generate_trajectory_adj, generate_traj4rp, generate_traj4nlp
from .model.preprocess.preprocess_spectral_cluster import generate_spectral_label
from .model.train import *
from .model.accident import *
from .model.train_route_plan import *
from .model.load_route_plan_model import *
from .model.train_loc_pred import *
from .model.load_loc_pred_model import *
from .model.utils import *
from .model.prediction import *
from .model.prediction.scripts.train_speed import *

# Create your views here.

class IntroductionView(LoginRequiredMixin, View):

    def get(self, request):
        print(request.session.get('is_login', None))
        template = "traffic/introduction.html"
        return render(request, template)

class RepresentationTrainView(LoginRequiredMixin, View):

    def get(self, request):
        form = RepresentationDataForm()
        template = "traffic/representation_train.html"
        return render(request, template, {"form": form})
    
    def post(self, request):

        form = RepresentationHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = RepresentationHyperparameter()
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
            app_name = "traffic"
            preprocessed_dir = "preprocessed"

            absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir)

            hparams.save_dir = os.path.join(root, app_name, "assign")
            if not os.path.exists(hparams.save_dir):
                os.makedirs(hparams.save_dir)
            hparams.struct_path = os.path.join(hparams.save_dir, "struct_assign.pkl")
            hparams.function_path = os.path.join(hparams.save_dir, "function_assign.pkl")
            hparams.road_embedding_path = os.path.join(hparams.save_dir, "road_embedding.pkl")

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

class RepresentationUploadView(LoginRequiredMixin, View):

    def post(self, request):

        data_type = request.POST.get("type")
        form = RepresentationDataForm(data=request.POST, files=request.FILES)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            new_file = RepresentationData()
            check = self.handle_uploaded_file(raw_file, data_type)
            print(f"check: {check}")
            if check == -1:
                data = {"error_msg": f"{data_type} file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = form.cleaned_data.get("type")
                new_file.save()

            data = []
            files = RepresentationData.objects.all().filter(type=data_type).order_by("-id")
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
        
    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "traffic"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        print(absolute_upload_dir_path)
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

class RepresentationPreView(LoginRequiredMixin, View):

    def get(self, request):
        template = "traffic/representation_pre.html"
        return render(request, template)

class SpeedPredicitonView(LoginRequiredMixin, View):

    template = "traffic/speed_prediction.html"

    def get(self, request):
        form = SpeedPredictionDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        print(f"POST data: {request.POST}")

        form = SpeedPredictionPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            print(f"hparams: {hparams}")

            print(os.getcwd())
            os.chdir('./traffic/model/prediction')
            predict()
            os.chdir('../../../')
            print(os.getcwd())

            output_path = os.path.join(os.getcwd(), "traffic/model/prediction/output.csv")
            df = pd.read_csv(output_path)
            with open(os.path.join(os.getcwd(), "traffic/model/prediction/entity_mapping.json"), "r") as f:
                entity_mapping_dict = json.load(f)
            speed_dict = dict()
            for id, group in df.groupby("id"):
                speed_dict[entity_mapping_dict[str(int(id))]] = list(group["speed"])[hparams["pred_time"]//5]
            return JsonResponse({"speed_dict": speed_dict})
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class SpeedPredictionUploadView(LoginRequiredMixin, View):

    def post(self, request):

        form = SpeedPredictionDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "speed_prediction"
            new_file = SpeedPredictionData()
            check, speed_dict = self.handle_uploaded_file(raw_file, data_type)
            print(check)
            if check == -1:
                data = {"error_msg": data_type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = data_type
                new_file.save()

            print(os.getcwd())
            os.chdir('./traffic/model/prediction')
            train()
            os.chdir('../../../')
            print(os.getcwd())

            return JsonResponse({"speed_dict": speed_dict})
        else:
            data = {"error_msg": "Only csv files are allowed."}
            return JsonResponse({"data": data})

    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "traffic"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        if not os.path.exists(absolute_upload_dir_path):
            os.makedirs(absolute_upload_dir_path)

        absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir, data_type)
        if not os.path.exists(absolute_preprocessed_dir_path):
            os.makedirs(absolute_preprocessed_dir_path)

        with open(absolute_upload_file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            speed_dict = {}
            data = pd.read_csv(absolute_upload_file_path)
            for id, group in data.groupby("entity_id"):
                speed_dict[id] = np.average(list(group["traffic_speed"]))
            print(speed_dict)
            return upload_file_path, speed_dict
        
        except Exception as e:
            print(e)
            return -1, -1

class RoutePlanView(LoginRequiredMixin, View):

    template = "traffic/route_plan.html"

    def get(self, request):
        form = RoutePlanDataForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = RoutePlanPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
        
            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "media/traffic/preprocessed/route_plan"
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")

            shortest_path = route_plan_pred(hparams)
            data = {"sp": shortest_path}
            return JsonResponse(data)
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class RoutePlanUploadView(LoginRequiredMixin, View):

    def post(self, request):

        form = RoutePlanDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "route_plan"
            new_file = RoutePlanData()
            check = self.handle_uploaded_file(raw_file, data_type)
            print(check)
            if check == -1:
                data = {"error_msg": data_type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = data_type
                new_file.save()
            
            data = []
            files = RoutePlanData.objects.all().order_by("-id")
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })

            return JsonResponse({"data": data})
        else:
            data = {"error_msg": "Only json files are allowed."}
            return JsonResponse({"data": data})

    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "traffic"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        if not os.path.exists(absolute_upload_dir_path):
            os.makedirs(absolute_upload_dir_path)

        absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir, data_type)
        if not os.path.exists(absolute_preprocessed_dir_path):
            os.makedirs(absolute_preprocessed_dir_path)

        with open(absolute_upload_file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        if data_type == "route_plan":
            try:
                route_plan_dataset = generate_traj4rp(absolute_upload_file_path)

                route_plan_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(route_plan_dataset_path, "wb") as f:
                    pickle.dump(route_plan_dataset, f)
            except Exception as e:
                print(e)
                return -1
        elif data_type == "next_loc":
            try:
                next_loc_dataset = generate_traj4nlp(absolute_upload_file_path)

                next_loc_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(next_loc_dataset_path, "wb") as f:
                    pickle.dump(next_loc_dataset, f)
            except Exception as e:
                print(e)
                return -1

        return upload_file_path

class RoutePlanTrainView(LoginRequiredMixin, View):

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = RoutePlanHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = RoutePlanHyperparameter()
            new_hyperparameter.epochs = form.cleaned_data.get("epochs")
            new_hyperparameter.batch_size = form.cleaned_data.get("batch_size")
            new_hyperparameter.lr = form.cleaned_data.get("lr")
            new_hyperparameter.dropout = form.cleaned_data.get("dropout")
            new_hyperparameter.save()

            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
            hparams.lp_learning_rate = new_hyperparameter.lr
            hparams.lp_clip = 1.0

            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "media/traffic/preprocessed/route_plan"
            hparams.route_plan_train = os.path.join(hparams.route_plan_dir, "train_set.pkl")
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")
            
            train_route_plan(hparams)

            return JsonResponse(data)
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class NextLocPredictionView(LoginRequiredMixin, View):

    template = "traffic/next_loc_prediction.html"

    def get(self, request):
        form = NextLocDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        print(f"POST data: {request.POST}")

        form = NextLocPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)
            print(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
        
            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.next_loc_dir = "media/traffic/preprocessed/next_loc"
            hparams.next_loc_model = os.path.join(hparams.next_loc_dir, "next_loc.model")
            print(f"hparams: {hparams}")

            next_loc = next_loc_pred(hparams)
            data = {"next_loc": next_loc}
            return JsonResponse(data)
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class NextLocPredictionUploadView(LoginRequiredMixin, View):

    def post(self, request):

        form = NextLocDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "next_loc"
            new_file = NextLocData()
            check = self.handle_uploaded_file(raw_file, data_type)
            print(check)
            if check == -1:
                data = {"error_msg": data_type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = data_type
                new_file.save()
            
            data = []
            files = NextLocData.objects.all().order_by("-id")
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })

            return JsonResponse({"data": data})
        else:
            data = {"error_msg": "Only json files are allowed."}
            return JsonResponse({"data": data})

    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "traffic"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        if not os.path.exists(absolute_upload_dir_path):
            os.makedirs(absolute_upload_dir_path)

        absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir, data_type)
        if not os.path.exists(absolute_preprocessed_dir_path):
            os.makedirs(absolute_preprocessed_dir_path)

        with open(absolute_upload_file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        if data_type == "route_plan":
            try:
                route_plan_dataset = generate_traj4rp(absolute_upload_file_path)

                route_plan_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(route_plan_dataset_path, "wb") as f:
                    pickle.dump(route_plan_dataset, f)
            except Exception as e:
                print(e)
                return -1
        elif data_type == "next_loc":
            try:
                next_loc_dataset = generate_traj4nlp(absolute_upload_file_path)

                next_loc_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(next_loc_dataset_path, "wb") as f:
                    pickle.dump(next_loc_dataset, f)
            except Exception as e:
                print(e)
                return -1

        return upload_file_path

class NextLocPredictionTrainView(LoginRequiredMixin, View):

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = NextLocHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = NextLocHyperparameter()
            new_hyperparameter.epochs = form.cleaned_data.get("epochs")
            new_hyperparameter.batch_size = form.cleaned_data.get("batch_size")
            new_hyperparameter.lr = form.cleaned_data.get("lr")
            new_hyperparameter.dropout = form.cleaned_data.get("dropout")
            new_hyperparameter.save()

            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
            hparams.lp_learning_rate = new_hyperparameter.lr
            hparams.lp_clip = 1.0

            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.next_loc_dir = "media/traffic/preprocessed/next_loc"
            hparams.next_loc_train = os.path.join(hparams.next_loc_dir, "train_set.pkl")
            hparams.next_loc_model = os.path.join(hparams.next_loc_dir, "next_loc.model")
            print(f"hparams: {hparams}")
            
            train_loc_pred(hparams)

            return JsonResponse({})
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class AccidentView(LoginRequiredMixin, View):

    def get(self, request):
        template = "traffic/accident.html"
        return render(request, template)
    
    def post(self, request):
        print(f"POST data: {request.POST}")

        form = AccidentPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            print(f"hparams: {hparams}")
        
            road_embeeding_path = "media/traffic/assign/road_embedding.pkl"
            with open(road_embeeding_path, "rb") as f:
                road_embeeding = pickle.load(f)
            road_embeeding_dict = dict()
            for i in range(len(road_embeeding)):
                road_embeeding_dict[i] = road_embeeding[i]

            accident_upload_path = "media/accident/upload/accident"
            history_speed_path = get_newest_file(accident_upload_path, "")
            with open(history_speed_path, "r") as f:
                history_speed = json.load(f)
            history_speed_new = dict()
            for key in history_speed:
                history_speed_new[int(key)] = history_speed[key]

            pred_speed = simulateAccident(road_embeeding_dict, history_speed_new, hparams.road, hparams.time)
            data = {"pred_speed": pred_speed}
            return JsonResponse(data)
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)
    
class AccidentUploadView(LoginRequiredMixin, View):

    def post(self, request):

        form = AccidentDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "accident"
            new_file = AccidentData()
            check, speed = self.handle_uploaded_file(raw_file, data_type)
            print(check)
            if check == -1:
                data = {"error_msg": data_type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = data_type
                new_file.save()

            return JsonResponse({"data": {}, "speed": speed})
        else:
            data = {"error_msg": "Only json files are allowed."}
            return JsonResponse({"data": data})

    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "accident"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        if not os.path.exists(absolute_upload_dir_path):
            os.makedirs(absolute_upload_dir_path)

        absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir, data_type)
        if not os.path.exists(absolute_preprocessed_dir_path):
            os.makedirs(absolute_preprocessed_dir_path)

        with open(absolute_upload_file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        try:
            with open(absolute_upload_file_path, "r") as f:
                speed = json.load(f)
        except Exception as e:
            print(e)
            return -1, -1

        return upload_file_path, speed
    
class RoutePlanView(LoginRequiredMixin, View):

    template = "traffic/route_plan.html"

    def get(self, request):
        form = RoutePlanDataForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = RoutePlanPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
        
            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "media/traffic/preprocessed/route_plan"
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")

            shortest_path = route_plan_pred(hparams)
            data = {"sp": shortest_path}
            return JsonResponse(data)
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)

class RoutePlanUploadView(LoginRequiredMixin, View):

    def post(self, request):

        form = RoutePlanDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "route_plan"
            new_file = RoutePlanData()
            check = self.handle_uploaded_file(raw_file, data_type)
            print(check)
            if check == -1:
                data = {"error_msg": data_type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = data_type
                new_file.save()
            
            data = []
            files = RoutePlanData.objects.all().order_by("-id")
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })

            return JsonResponse({"data": data})
        else:
            data = {"error_msg": "Only json files are allowed."}
            return JsonResponse({"data": data})

    def handle_uploaded_file(self, file, data_type):

        root = "media"
        app_name = "traffic"

        upload_dir = "upload"
        preprocessed_dir = "preprocessed"

        file_name = file.name
        upload_file_path = os.path.join(app_name, upload_dir, data_type, file_name)
        absolute_upload_file_path = os.path.join(root, upload_file_path)

        absolute_upload_dir_path = os.path.dirname(absolute_upload_file_path)
        if not os.path.exists(absolute_upload_dir_path):
            os.makedirs(absolute_upload_dir_path)

        absolute_preprocessed_dir_path = os.path.join(root, app_name, preprocessed_dir, data_type)
        if not os.path.exists(absolute_preprocessed_dir_path):
            os.makedirs(absolute_preprocessed_dir_path)

        with open(absolute_upload_file_path, "wb+") as f:
            for chunk in file.chunks():
                f.write(chunk)

        if data_type == "route_plan":
            try:
                route_plan_dataset = generate_traj4rp(absolute_upload_file_path)

                route_plan_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(route_plan_dataset_path, "wb") as f:
                    pickle.dump(route_plan_dataset, f)
            except Exception as e:
                print(e)
                return -1
        elif data_type == "next_loc":
            try:
                next_loc_dataset = generate_traj4nlp(absolute_upload_file_path)

                next_loc_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
                with open(next_loc_dataset_path, "wb") as f:
                    pickle.dump(next_loc_dataset, f)
            except Exception as e:
                print(e)
                return -1

        return upload_file_path

class RoutePlanTrainView(LoginRequiredMixin, View):

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = RoutePlanHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = RoutePlanHyperparameter()
            new_hyperparameter.epochs = form.cleaned_data.get("epochs")
            new_hyperparameter.batch_size = form.cleaned_data.get("batch_size")
            new_hyperparameter.lr = form.cleaned_data.get("lr")
            new_hyperparameter.dropout = form.cleaned_data.get("dropout")
            new_hyperparameter.save()

            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = RepresentationHyperparameter.objects.latest("id")
            # print(f"road_network_params: {road_network_params}")
            hparams.road_num = road_network_params.road_num
            hparams.road_dim = road_network_params.road_dim
            hparams.region_num = road_network_params.region_num
            hparams.region_dim = road_network_params.region_dim
            hparams.zone_num = road_network_params.zone_num
            hparams.zone_dim = road_network_params.zone_dim
            hparams.hidden_dims = road_network_params.road_dim

            hparams.length_dim = 32
            hparams.length_num = 2200
            hparams.lp_learning_rate = new_hyperparameter.lr
            hparams.lp_clip = 1.0

            road_network_path = "media/traffic/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/traffic/assign/struct_assign.pkl"
            hparams.function_path = "media/traffic/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "media/traffic/preprocessed/route_plan"
            hparams.route_plan_train = os.path.join(hparams.route_plan_dir, "train_set.pkl")
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")
            
            train_route_plan(hparams)

            return JsonResponse({})
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)


