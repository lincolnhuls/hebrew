from django.shortcuts import render, HttpResponse
from django.http import JsonResponse
from .models import UserInformation
import firebase_admin
from firebase_admin import auth, credentials
import json
import os
import time

if not firebase_admin._apps:
    cred = credentials.Certificate(os.environ["GOOGLE_APPLICATION_CREDENTIALS"])
    firebase_admin.initialize_app(cred)
    
# Helper for timing issues with firebase tokens
def verify_with_retry(token, max_retries=3, base_delay=.25):
    for attempt in range(max_retries):
        try:
            return firebase_admin.auth.verify_id_token(token)
        except Exception as e:
            msg = str(e)
            if "Token used too early" in msg and attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            raise

# Create your views here.
def home(request):
    return render(request, "users/home.html")

def users(request):
    items = UserInformation.objects.all()
    return render(request, "users/users.html", {"users": items})

def user_sessions(request):
    if request.method == "POST":
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            data = {
                'ok': False,
                'error': 'Authorization header missing'
            }
            return JsonResponse(data, status=401)
        elif not auth_header.startswith('Bearer '):
            data = {
                'ok': False,
                'error': 'Invalid authorization header format'
            }
            return JsonResponse(data, status=401)
        else:
            token = auth_header.split(' ')[1].strip()
            if not token:
                data = {
                    'ok': False,
                    'error': 'Token missing'
                }
                return JsonResponse(data, status=401)
            else:
                try:
                    user_token = verify_with_retry(token)
                    user_uid = user_token['uid']
                    user_email = user_token.get('email', None)
                    user_name = user_token.get('name', None)
                    if not user_uid:
                        data = {
                            'ok': False,
                            'error': 'Invalid token'
                        }
                        return JsonResponse(data, status=401)
                    if not request.body:
                        body_data = {}
                        name_from_body = ""
                    else:
                        try: 
                            body_data = json.loads(request.body.decode('utf-8'))
                        except json.JSONDecodeError:
                            data = {
                                'ok': False,
                                'error': 'Invalid JSON'
                            }
                            return JsonResponse(data, status=400)
                        name_from_body = body_data.get('name', "").strip()
                    changed = False
                    user, created = UserInformation.objects.get_or_create(
                        firebase_uid = user_uid,
                        defaults={
                            'name': name_from_body,
                            'email': user_email}
                    )
                    if created and name_from_body == "":
                        data = {
                            'ok': False,
                            'error': 'Name is required for new users'
                        }
                        return JsonResponse(data, status=400)
                    if not created:
                        if user.name == "" and name_from_body:
                            user.name = name_from_body
                            changed = True
                        if user.email == "" and user_email:
                            user.email = user_email
                            changed = True
                        if changed:
                            user.save()
                    request.session['firebase_uid'] = user.firebase_uid
                    request.session['username'] = user.name
                    request.session['email'] = user.email
                    data = {
                        'ok': True,
                        'user': {
                            'firebase_uid': user.firebase_uid,
                            'name': user.name,
                            'email': user.email
                        },
                        'created': created
                    }
                    return JsonResponse(data, status=200)
                except Exception as e:
                    data = {
                        'ok': False,
                        'error': 'Error with token',
                        'details': str(e)
                    }
                    return JsonResponse(data, status=401)
    else:
        data = {
            'ok': False,
            'error': 'Only POST requests are allowed'
        }
        return JsonResponse(data, status=405)
    
def user_logout(request):
    if request.method == "POST":
        try:
            request.session.flush()
            data = {
                'ok': True,
                'message': 'User logged out successfully'
            }
            return JsonResponse(data, status=200)
        except Exception as e:
            data = {
                'ok': False,
                'error': 'Error logging out user',
                'details': str(e)
            }
            return JsonResponse(data, status=500)
    else:
        data = {
            'ok': False,
            'error': 'Only POST requests are allowed'
        }
        return JsonResponse(data, status=405)