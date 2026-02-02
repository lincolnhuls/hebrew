from django.shortcuts import render, redirect
from django.http import HttpResponse

# Create your views here.
def home(request):
    if request.session.get('firebase_uid'):
        return redirect('main:dashboard')
    return render(request, "main/home.html")

def dashboard(request): 
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")
    return render(request, "main/dashboard.html")


def settings_page(request):
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")
    return render(request, "main/settings.html")