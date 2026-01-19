from django.contrib import admin
from .models import ToDoItem, UserInformation

# Register your models here.
admin.site.register(ToDoItem)
admin.site.register(UserInformation)