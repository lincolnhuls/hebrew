from django.db import models
    
class UserInformation(models.Model):
    firebase_uid = models.CharField(max_length=200)
    name = models.CharField(max_length=50)
    email = models.CharField(max_length=50)
    
    def __str__(self):
        return self.name