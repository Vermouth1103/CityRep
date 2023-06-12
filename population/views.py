from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.

class IntroductionView(LoginRequiredMixin, View):

    def get(self, request):
        template = "population/introduction.html"
        return render(request, template)

class RepresentationTrainView(LoginRequiredMixin, View):

    def get(self, request):
        template = "population/representation_train.html"
        return render(request, template)

class RepresentationPreView(LoginRequiredMixin, View):

    def get(self, request):
        template = "population/representation_pre.html"
        return render(request, template)