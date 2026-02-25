from django.http import JsonResponse
import firebase_admin 
from firebase_admin import credentials, auth
import os
import time

if not firebase_admin._apps:
    cred_path = os.environ.get("GOOGLE_APPLICATION_CREDENTIALS")
    json_str = os.environ.get("FIREBASE_CREDENTIALS_JSON")
    if json_str:
        import tempfile
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            f.write(json_str)
            cred_path = f.name
        os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = cred_path
    if not cred_path:
        raise RuntimeError("GOOGLE_APPLICATION_CREDENTIALS or FIREBASE_CREDENTIALS_JSON is not set")
    if not os.path.exists(cred_path):
        raise RuntimeError(f"Firebase credentials file not found: {cred_path}")
    cred = credentials.Certificate(cred_path)
    firebase_admin.initialize_app(cred)  

def error_response(message, status=400, details=None):
    data = { 'ok': False, 'error': message }
    if details is not None:
        data['details'] = details
    return JsonResponse(data, status=status)

# Helper for timing issues with firebase tokens
def verify_with_retry(token, max_retries=7, base_delay=.25):
    for attempt in range(max_retries):
        try:
            return firebase_admin.auth.verify_id_token(token)
        except Exception as e:
            msg = str(e)
            if "Token used too early" in msg and attempt < max_retries - 1:
                time.sleep(base_delay * (2 ** attempt))
                continue
            raise