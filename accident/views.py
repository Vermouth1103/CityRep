from django.shortcuts import render
from django.views import View
from .forms import AccidentDataForm

# Create your views here.
class AccidentDes(View):

    def get(self, request):
        template = "accident/accident_des.html"
        return render(request, template)

class AccidentPre(View):

    def get(self, request):
        form = AccidentDataForm()
        template = "accident/accident_pre.html"
        return render(request, template)