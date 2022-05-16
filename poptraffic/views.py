from django.shortcuts import render, redirect
from django.views import View
from django.http import JsonResponse
from django.template.defaultfilters import filesizeformat
from .forms import PopTrafficDataForm
from .models import PopTrafficData
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

    # def post(self, request):
    #     _type = request.POST["type"]
    #     print(_type)

    #     if _type == "road_network":
    #         form = RoadNetworkUpload(request.POST, request.FILES)
    #         # print(form.errors)
    #         if form.is_valid():
    #             # get cleaned data
    #             raw_file = form.cleaned_data.get("file")
    #             new_file = RoadNetworkData()
    #             new_file.file = handle_uploaded_file(raw_file, _type)
    #             new_file.save()
    #             # return render(request, self.template, {'form': form})
    #             files = RoadNetworkData.objects.all().order_by('-id')
    #             data = []
    #             print(files[0].file.url)
    #             print(files[0].file.size)
    #             for file in files:
    #                 data.append({
    #                     "url": file.file.url,
    #                     "size": filesizeformat(file.file.size)
    #                     })
    #             return JsonResponse(data, safe=False)
    #         else:
    #             data = {'error_msg': "Only jpg, pdf and xlsx files are allowed."}
    #             return JsonResponse(data)
    #     elif _type == "trajectory":
    #         form = TrajectoryUpload(request.POST, request.FILES)
    #         if form.is_valid():
    #             # get cleaned data
    #             raw_file = form.cleaned_data.get("file")
    #             new_file = TrajectoryData()
    #             new_file.file = handle_uploaded_file(raw_file, _type)
    #             new_file.save()
    #             return render(request, self.template, {'form': form})
    #     elif _type == "POI":
    #         form = POIUpload(request.POST, request.FILES)
    #         if form.is_valid():
    #             # get cleaned data
    #             raw_file = form.cleaned_data.get("file")
    #             new_file = POIData()
    #             new_file.file = handle_uploaded_file(raw_file, _type)
    #             new_file.save()
    #             return render(request, self.template, {'form': form})
    #     return JsonResponse({'error_msg': 'only POST method accpeted.'})

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

