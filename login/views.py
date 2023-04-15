from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login
from django.views import View
from django.contrib import messages

from .forms import RegisterForm
from django.contrib.auth.forms import UserCreationForm

# Create your views here.
class LoginView(View):
    
    template = "login/login.html"

    def get(self, request):
        # if request.session.get('is_login', None):
        #     return redirect('/main/')
        return render(request, self.template)
    
    def post(self, request):
        username = request.POST['username']
        password = request.POST['password']
        print(username, password)
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # 如果用户存在，且用户名和密码正确，则登录用户
            login(request, user)
            request.session['is_login'] = True
            return redirect("/main/")
        else:
            # 如果用户名和密码不正确，则返回登录页面，并显示错误消息
            message = "用户名或者密码错误"
            return render(request, self.template, {'message': message})


class RegisterView(View):

    template = "login/register.html"

    def get(self, request):
        register_form = RegisterForm()
        return render(request, self.template, {"register_form": register_form})

    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True
            user.save()
            messages.success(request, '注册成功！')
            return redirect('/login/')
        else:
            register_form = RegisterForm()
            error_msg = ''
            for field in form:
                if field.errors:
                    error_msg += f"{field.label}: {field.errors.as_text()}\n"
            messages.error(request, error_msg)
            return render(request, self.template, {"register_form": register_form})
        
    
class LogoutView(View):

    def post(self, request):
        if not request.session.get('is_login', None):
            # 如果本来就未登录，也就没有登出一说
            return redirect("/login/")
        request.session.flush()
        # 或者使用下面的方法
        # del request.session['is_login']
        # del request.session['user_id']
        # del request.session['user_name']
        return redirect("/login/")