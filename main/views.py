from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from django.views import View


# Create your views here.
class IndexView(View):
    
    def get(self, request):
        template = "main/index.html"
        return render(request, template)
