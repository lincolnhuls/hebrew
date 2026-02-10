from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(Lesson)
admin.site.register(LessonSession)
admin.site.register(LessonAnswer)
admin.site.register(HebrewLetter)