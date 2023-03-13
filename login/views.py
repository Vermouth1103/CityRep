from django.shortcuts import render
from django.views import View


# Create your views here.
class LoginView(View):

    def get(self, request):
        template = "login/login.html"
        return render(request, template)