from django.shortcuts import render
from django.views import View
from .models import RoutePlanData, RoutePlanHyperparameter, NextLocData, NextLocHyperparameter
from .forms import RoutePlanDataForm, RoutePlanHyperparameterForm, NextLocDataForm, NextLocHyperparameterForm

# Create your views here.
class RoutePlanDes(View):
    
    def get(self, request):
        template = "indtraffic/routeplan_des.html"
        return render(request, template)

class RoutePlanPre(View):

    template = "indtraffic/routeplan_pre.html"

    def get(self, request):
        form = RoutePlanDataForm()
        return render(request, self.template, {"form": form})

    def post(self, request):
        pass

class NextLocDes(View):

    def get(self, request):
        template = "indtraffic/nextloc_des.html"
        return render(request, template)

class NextLocPre(View):

    template = "indtraffic/nextloc_pre.html"

    def get(self, request):
        form = NextLocDataForm()
        return render(request, self.template, {"form": form})
    
    def post(self, request):
        pass