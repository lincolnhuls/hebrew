from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import UserInformation
import firebase_admin
from firebase_admin import auth, credentials
import json
import os
import time
import os.path



# Create your views here.

