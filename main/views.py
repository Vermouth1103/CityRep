from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin


# Create your views here.
class IndexView(LoginRequiredMixin, View):
        
    def get(self, request):
        template = "main/index.html"
        return render(request, template)
