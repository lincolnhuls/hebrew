from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, auth
import json
import os
import time


def _ensure_firebase_initialized():
    """Initialize Firebase Admin lazily so app boot is not blocked by missing creds."""
    if firebase_admin._apps:
        return

    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    json_str = os.environ.get("FIREBASE_CREDENTIALS_JSON")

    if json_str:
        try:
            cred_dict = json.loads(json_str)
        except json.JSONDecodeError as e:
            raise RuntimeError(f"FIREBASE_CREDENTIALS_JSON is not valid JSON: {e}") from e
        cred = credentials.Certificate(cred_dict)
        firebase_admin.initialize_app(cred)
        return

    if cred_path and os.path.exists(cred_path):
        cred = credentials.Certificate(cred_path)
        firebase_admin.initialize_app(cred)
        return

    raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS_JSON is not set")


def error_response(message, status=400, details=None):
    data = {'ok': False, 'error': message}
    if details is not None:
        data['details'] = details
    return JsonResponse(data, status=status)


# Helper for timing issues with firebase tokens
def verify_with_retry(token, max_retries=7, base_delay=.25):
    _ensure_firebase_initialized()
    for attempt in range(max_retries):
        try:
            return auth.verify_id_token(token)
        except Exception as e:
            msg = str(e)
            if "Token used too early" in msg and attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            raise
