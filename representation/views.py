from django.shortcuts import render
from django.views import View
from .models import Data, Hyperparameter
from .forms import DataForm, HyperparameterForm

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

class ModelPreView(View):

    def get(self, request):
        template = "representation/model_pre.html"
        return render(request, template)