from django.shortcuts import render
from django.http import HttpResponse

# Create your views here.
def home(request):
    return render(request, "main/home.html")

def dashboard(request): 
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")
    return render(request, "main/dashboard.html")