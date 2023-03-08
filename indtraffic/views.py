from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .models import RoutePlanData, RoutePlanHyperparameter, NextLocData, NextLocHyperparameter
from .forms import RoutePlanDataForm, RoutePlanHyperparameterForm, NextLocDataForm, NextLocHyperparameterForm
from representation.models import Hyperparameter

from .model.preprocess.preprocess_trajectory import generate_traj4rp
from .model.train_route_plan import *
from .model.utils import *

def handle_uploaded_file(file, data_type):

    root = "media"
    app_name = "indtraffic"

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
        route_plan_dataset = generate_traj4rp(absolute_upload_file_path)

        route_plan_dataset_path = os.path.join(absolute_preprocessed_dir_path, "train_set.pkl")
        with open(route_plan_dataset_path, "wb") as f:
            pickle.dump(route_plan_dataset, f)
    except Exception as e:
        print(e)
        return -1

    return upload_file_path

# Create your views here.
class RoutePlanDesView(View):
    
    def get(self, request):
        template = "indtraffic/routeplan_des.html"
        return render(request, template)

class RoutePlanPreView(View):

    template = "indtraffic/routeplan_pre.html"

    def get(self, request):
        form = RoutePlanDataForm()
        return render(request, self.template, {"form": form})

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

            road_network_params = Hyperparameter.objects.latest("id")
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

            road_network_path = "media/representation/preprocessed"
            hparams.adj = get_newest_file(road_network_path, "graph")
            hparams.node_features = get_newest_file(road_network_path, "features")

            hparams.struct_path = "media/representation/assign/struct_assign.pkl"
            hparams.function_path = "media/representation/assign/function_assign.pkl"

            hparams.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
            hparams.route_plan_dir = "media/indtraffic/preprocessed/route_plan"
            hparams.route_plan_train = os.path.join(hparams.route_plan_dir, "train_set.pkl")
            hparams.route_plan_model = os.path.join(hparams.route_plan_dir, "route_plan.model")
            print(f"hparams: {hparams}")
            
            train_route_plan(hparams)

            form = RoutePlanDataForm()
            return render(request, self.template, {"form": form})
        else:
            data = {"error_msg": "Hyper parameter set invalid."}
            return JsonResponse(data)
        
class RoutePlanUploadView(View):

    def post(self, request):

        form = RoutePlanDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "route_plan"
            new_file = RoutePlanData()
            check = handle_uploaded_file(raw_file, data_type)
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
        
class NextLocDesView(View):

    def get(self, request):
        template = "indtraffic/nextloc_des.html"
        return render(request, template)

class NextLocPreView(View):

    template = "indtraffic/nextloc_pre.html"

    def get(self, request):
        form = NextLocDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        pass