from django.shortcuts import render
from django.views.decorators.csrf import ensure_csrf_cookie
from ..models import UserInformation
from django.core.paginator import Paginator
from lessons.constants import USERS_PER_PAGE

def home(request):
    """Render the users app home page."""
    return render(request, "users/home.html")

@ensure_csrf_cookie
def users(request):
    """List all users with pagination."""
    user_list = UserInformation.objects.all().order_by('id')
    paginator = Paginator(user_list, USERS_PER_PAGE)  
    
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, "users/users.html", {'users': page_obj})
