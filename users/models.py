from django.db import models
    
class UserInformation(models.Model):
    firebase_uid = models.CharField(max_length=200, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, db_index=True)
    
    def __str__(self):
        return self.name