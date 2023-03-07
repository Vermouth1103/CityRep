from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .forms import PopTrafficDataForm, PopTrafficHyperparameterForm, PopTrafficRoutePlanDataForm, PopTrafficRoutePlanHyperparameterForm
from .models import PopTrafficData, PopTrafficHyperparameter, PopTrafficRoutePlanData, PopTrafficRoutePlanHyperparameter

from .model.preprocess.preprocess_roadnetwork import generate_graph, generate_features
from .model.preprocess.preprocess_trajectory import generate_trajectory_adj, generate_traj4rp
from .model.preprocess.preprocess_spectral_cluster import generate_spectral_label
from .model.train import *
from .model.train_route_plan import *

# Create your views here.
def handle_uploaded_file(file, _type, road_network_path=""):
    
    # preprocess check
    if _type == "road_network":
        try:
            file_name = file.name
            file_path = os.path.join(_type, file_name)
            absolute_file_path = os.path.join('media', _type, file_name)

            directory = os.path.dirname(absolute_file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(absolute_file_path, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            generate_graph(absolute_file_path, _type)
            generate_features(absolute_file_path, _type)
        except:
            print(e)
            return -1
        
    elif _type == "trajectory":
        try:
            file_name = file.name
            file_path = os.path.join(_type, file_name)
            absolute_file_path = os.path.join('media', _type, file_name)

            directory = os.path.dirname(absolute_file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(absolute_file_path, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            generate_trajectory_adj(absolute_file_path, _type, road_network_path)
        except Exception as e:
            print(e)
            return -1
        
    elif _type == "route_plan":
        try:
            file_name = file.name
            file_path = os.path.join(_type, "upload", file_name)
            absolute_file_path = os.path.join('media',file_path)

            directory = os.path.dirname(absolute_file_path)
            if not os.path.exists(directory):
                os.makedirs(directory)

            with open(absolute_file_path, "wb+") as f:
                for chunk in file.chunks():
                    f.write(chunk)
            route_plan_dataset = generate_traj4rp(absolute_file_path)

            save_dir = os.path.join("media", _type, "preprocessed")
            if not os.path.exists(save_dir):
                os.makedirs(save_dir)
            with open(os.path.join(save_dir, "train_set.pkl"), "wb") as f:
                pickle.dump(route_plan_dataset, f)
        except Exception as e:
            print(e)
            return -1

    return file_path

class PopTrafficModelDesView(View):
    
    def get(self, request):
        template = "poptraffic/poptraffic_model_des.html"
        return render(request, template)

class PopTrafficDataDesView(View):

    def get(self, request):
        template = "poptraffic/poptraffic_data_des.html"
        return render(request, template)

class PopTrafficInputModelView(View):

    def get(self, request):
        form = PopTrafficDataForm()
        template = "poptraffic/poptraffic_input_model.html"
        return render(request, template,  {'form': form})

# handling AJAX requests
class PopTrafficUploadData(View):

    def post(self, request):
        _type = request.POST.get('type')

        road_network_path = request.POST.get('road_network_path')
        print(f"road_network_path: {road_network_path}")

        form = PopTrafficDataForm(data=request.POST, files=request.FILES)
        print(form.errors)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            new_file = PopTrafficData()
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

            files = PopTrafficData.objects.all().filter(type=_type).order_by('-id')
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

class PopTrafficTrain(View):

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = PopTrafficHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = PopTrafficHyperparameter()
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

class PopTrafficDownstreamTask(View):

    template = "poptraffic/poptraffic_downstream_task.html"
    
    def get(self, request):
        form = PopTrafficRoutePlanDataForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        print(f"POST data: {request.POST}")

        form = PopTrafficRoutePlanDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            print(form.cleaned_data)
            raw_file = form.cleaned_data.get("file")
            _type = "route_plan"
            print(f"raw_file: {raw_file}, type: {_type}")
            new_file = PopTrafficRoutePlanData()
            check = handle_uploaded_file(raw_file, _type)
            print(check)
            if check == -1:
                data = {"error_msg": _type+" file invalid."}
                return JsonResponse(data)
            else:
                new_file.file = check
                new_file.type = _type
                new_file.save()
            files = PopTrafficRoutePlanData.objects.all().order_by('-id')
            data = []
            for file in files:
                data.append({
                    "url": file.file.url,
                    "size": filesizeformat(file.file.size),
                    "type": file.type,
                    })

            form = PopTrafficRoutePlanDataForm()
            return render(request, self.template, {"form": form, "data": data})
        else:
            form = PopTrafficRoutePlanDataForm()
            data = {'error_msg': "Only json files are allowed."}
            return render(request, self.template, {"data": data})

class PopTrafficRoutePlan(View):
    
    def post(self, request):
        print(f"POST data: {request.POST}")

        form = PopTrafficRoutePlanHyperparameterForm(data=request.POST)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = PopTrafficRoutePlanHyperparameter()
            new_hyperparameter.epochs = form.cleaned_data.get("epochs")
            new_hyperparameter.batch_size = form.cleaned_data.get("batch_size")
            new_hyperparameter.lr = form.cleaned_data.get("lr")
            new_hyperparameter.dropout = form.cleaned_data.get("dropout")
            new_hyperparameter.save()

            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            road_network_params = PopTrafficHyperparameter.objects.latest("id")
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

            road_network_path = "./media/preprocessed_road_network/"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "./media/assign/struct_assign.pkl"
            hparams.function_path = "./media/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "./media/route_plan/preprocessed"
            hparams.route_plan_train = os.path.join(hparams.route_plan_dir, "train_set.pkl")
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")
            
            train_route_plan(hparams)

            form = PopTrafficRoutePlanDataForm()
            return render(request, self.template, {"form": form})
        else:
            data = {'error_msg': "Hyper parameter set invalid."}
            return JsonResponse(data)