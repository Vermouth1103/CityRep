from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .forms import PopTrafficDataForm, PopTrafficHyperparameterForm
from .models import PopTrafficData, PopTrafficHyperparameter
import os
import time

# Create your views here.

def handle_uploaded_file(file, _type):
    import time

    ext = file.name.split('.')[-1]
    _time = str(int(time.time()))
    file_name = _time + '_' + file.name

    file_path = os.path.join(_type, file_name)
    absolute_file_path = os.path.join('media', _type, file_name)

    directory = os.path.dirname(absolute_file_path)
    if not os.path.exists(directory):
        os.makedirs(directory)

    with open(absolute_file_path, "wb+") as f:
        for chunk in file.chunks():
            f.write(chunk)
    
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
        return render(request, "poptraffic/poptraffic_input_model.html",  {'form': form})

# handling AJAX requests
class PopTrafficUploadData(View):

    def post(self, request):
        _type = request.POST.get('type')
        print(request.POST)
        print(_type)

        # if _type == "road_network":
        form = PopTrafficDataForm(data=request.POST, files=request.FILES)
        print(form.errors)
        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            new_file = PopTrafficData()
            new_file.file = handle_uploaded_file(raw_file, _type)
            new_file.type = form.cleaned_data.get("type")
            new_file.save()
            # return render(request, self.template, {'form': form})
            files = PopTrafficData.objects.all().filter(type=_type).order_by('-id')
            data = []
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
                data = {'error_msg': "Only txt files are allowed."}
            elif _type == "POI":
                data = {'error_msg': "Only csv files are allowed."}
            else:
                data = {'error_msg': "Only json, txt, csv files are allowed."}
            return JsonResponse(data)

class PopTrafficTrain(View):

    def post(self, request):
        print(request.POST)

        form = PopTrafficHyperparameterForm(data=request.POST)
        print(form.errors)

        if form.is_valid():
            # get cleaned data
            new_hyperparameter = PopTrafficHyperparameter()
            new_hyperparameter.road_num = form.cleaned_data.get("road_num")
            new_hyperparameter.road_dim = form.cleaned_data.get("road_dim")
            new_hyperparameter.region_num = form.cleaned_data.get["region_num"]
            new_hyperparameter.region_dim = form.cleaned_data.get["region_dim"]
            new_hyperparameter.zone_num = form.cleaned_data.get["zone_num"]
            new_hyperparameter.zone_dim = form.cleaned_data.get["zone_dim"]
            new_hyperparameter.epochs = form.cleaned_data.get["epochs"]
            new_hyperparameter.batch_size = form.cleaned_data.get["batch_size"]
            new_hyperparameter.lr = form.cleaned_data.get["lr"]
            new_hyperparameter.dropout = form.cleaned_data.get["dropout"]
            new_hyperparameter.save()

            