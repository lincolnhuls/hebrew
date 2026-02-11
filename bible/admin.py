from django.contrib import admin
from .models import BibleBook, BibleChapter, BibleVerse

# Register your models here.
admin.site.register(BibleBook)
admin.site.register(BibleChapter)
admin.site.register(BibleVerse)
