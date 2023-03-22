from django.shortcuts import render
from django.views import View

# Create your views here.
class IntroductionView(View):

    def get(self, request):
        template = "economy/introduction.html"
        return render(request, template)

class RepresentationTrainView(View):

    def get(self, request):
        template = "economy/introduction.html"
        return render(request, template)

class RepresentationPreView(View):

    def get(self, request):
        template = "economy/introduction.html"
        return render(request, template)