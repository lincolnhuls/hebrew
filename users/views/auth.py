from ..utils import error_response, verify_with_retry
from ..models import UserInformation
from django.http import JsonResponse
import json
import firebase_admin
from firebase_admin import credentials
import os
import time

def user_sessions(request):
    if request.method == "POST":
        auth_header = request.META.get('HTTP_AUTHORIZATION')
        if not auth_header:
            return error_response("Authorization header missing", status=401)
        elif not auth_header.startswith('Bearer '):
            return error_response("Invalid authorization header format", status=401)
        else:
            token = auth_header.split(' ')[1].strip()
            if not token:
                return error_response("Token missing", status=401)
            else:
                try:
                    user_token = verify_with_retry(token)
                    user_uid = user_token['uid']
                    user_email = user_token.get('email', None)
                    user_name = user_token.get('name', None)

                    if not user_uid:
                        return error_response("Invalid token", status=401)

                    # Parse body (optional)
                    if not request.body:
                        body_data = {}
                        name_from_body = ""
                    else:
                        try:
                            body_data = json.loads(request.body.decode('utf-8'))
                        except json.JSONDecodeError:
                            return error_response("Invalid JSON", status=400)
                        name_from_body = body_data.get('name', "").strip()

                    # Prevent base.js "refresh session" calls from creating blank users
                    if not name_from_body:
                        existing = UserInformation.objects.filter(firebase_uid=user_uid).exists()
                        if not existing:
                            return error_response("Name is required for new users", status=400)

                    changed = False

                    user, created = UserInformation.objects.get_or_create(
                        firebase_uid=user_uid,
                        defaults={
                            'name': name_from_body,
                            'email': user_email
                        }
                    )

                    # If created via auth.js, name must be present (should already be enforced above)
                    if created and not name_from_body:
                        return error_response("Name is required for new users", status=400)

                    # Update missing fields on existing users
                    if not created:
                        if (not user.name) and name_from_body:
                            user.name = name_from_body
                            changed = True
                        if (not user.email) and user_email:
                            user.email = user_email
                            changed = True
                        if changed:
                            user.save()

                    # Store canonical user info in Django session
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
                    return error_response("Error verifying token", status=401, details=str(e))
    else:
        return error_response("Only POST requests are allowed", status=405)

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
            return error_response("Error logging out user", status=500, details=str(e))
    else:
        return error_response("Only POST requests are allowed", status=405)