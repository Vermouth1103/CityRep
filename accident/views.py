from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .models import AccidentData
from .forms import AccidentDataForm, AccidentPredForm
import os
import json
from .model.accident import *
from .model.utils import *


def handle_uploaded_file(file, data_type):

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

# Create your views here.
class AccidentDesView(View):

    def get(self, request):
        template = "accident/accident_des.html"
        return render(request, template)

class AccidentPreView(View):

    def get(self, request):
        template = "accident/accident_pre.html"
        return render(request, template)
    
    def post(self, request):
        print(f"POST data: {request.POST}")

        form = AccidentPredForm(data=request.POST)

        if form.is_valid():
            hparams = form.cleaned_data
            hparams = dict_to_object(hparams)

            print(f"hparams: {hparams}")
        
            road_embeeding_path = "media/representation/assign/road_embedding.pkl"
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
    
class AccidentUploadView(View):

    def post(self, request):

        form = AccidentDataForm(data=request.POST, files=request.FILES)

        if form.is_valid():
            # get cleaned data
            raw_file = form.cleaned_data.get("file")
            data_type = "accident"
            new_file = AccidentData()
            check, speed = handle_uploaded_file(raw_file, data_type)
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