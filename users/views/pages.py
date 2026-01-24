from django.shortcuts import render
from ..models import UserInformation
from django.core.paginator import Paginator

def home(request):
    return render(request, "users/home.html")

def users(request):
    user_list = UserInformation.objects.all().order_by('id')
    paginator = Paginator(user_list, 25)  
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "users/users.html", {'users': page_obj})
