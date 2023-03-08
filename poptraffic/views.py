from django.shortcuts import render, redirect
from django.views import View
from .forms import SpeedPredictionDataForm, FlowPredictionDataForm


# Create your views here.
class SpeedPredictionDes(View):

    def get(self, request):
        template = "poptraffic/speedprediction_des.html"
        return render(request, template)

class SpeedPredictionPre(View):

    template = "poptraffic/speedprediction_pre.html"

    def get(self, request):
        form = SpeedPredictionDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        pass

class FlowPredictionDes(View):

    def get(self, request):
        template = "poptraffic/flowprediction_des.html"
        return render(request, template)

class FlowPredictionPre(View):

    template = "poptraffic/flowprediction_pre.html"

    def get(self, request):
        form = FlowPredictionDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        pass

