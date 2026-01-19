from django.db import models

# Create your models here.
class ToDoItem(models.Model):
    title = models.CharField(max_length=200)
    completed = models.BooleanField(default=False) 
    
class UserInformation(models.Model):
    firebase_uid = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)