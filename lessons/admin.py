from django.contrib import admin
from .models import Lesson, LessonSession, LessonAnswer, HebrewLetter, HebrewVowel

# Register your models here.
admin.site.register(Lesson)
admin.site.register(LessonSession)
admin.site.register(LessonAnswer)
admin.site.register(HebrewLetter)
admin.site.register(HebrewVowel)