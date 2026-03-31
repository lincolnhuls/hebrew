import logging

from django.conf import settings
from django.core.mail import send_mail
from django.http import JsonResponse
import firebase_admin
from firebase_admin import credentials, auth
import json
import os
import time
from users.models import LearningPreferences


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


logger = logging.getLogger(__name__)


def send_learning_goals_confirmation(user, preferences):
    """Send an email confirming user's learning goals"""
    if not user.email:
        logger.info("Skipping confirmation email: user %s has no email", user.firebase_uid)
        return

    freq_labels = dict(LearningPreferences.REMINDER_FREQUENCY_CHOICES)
    freq_display = freq_labels.get(preferences.reminder_frequency, preferences.reminder_frequency)
    time_str = preferences.reminder_time.strftime("%H:%M") if preferences.reminder_time else "Not set"
    
    subject = "Your Biblical Hebrew Learning Goals"
    body = f"""Hi {user.name or 'there'},
    
Your learning goals have been saved:

• Lesson per day: {preferences.daily_lessons_target}
• Reminder emails: {'On' if preferences.reminder_enabled else 'Off'}
• How often: {freq_display}
• Reminder time: {time_str}
• Timezone: {preferences.timezone}
    
You can change these anytime from the Settings page.

Happy learning!
Hebrew for Everyone
"""

    try:
        sent = send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Confirmation email send raised an error for %s", user.email)
        return
    if not sent:
        logger.warning("Confirmation email was not accepted by backend for %s", user.email)


def send_reminder_email(user, preferences):
    """Send a 'time to study' reminder email. Updates last_reminder_sent_at on success"""
    if not user.email or not preferences.reminder_time:
        return False
    subject = "Time to study Biblical Hebrew!"
    body = f"""Hi {user.name or 'there'},
    
A quick reminder: it's time for your daily Hebrew lesson!

Your goal: {preferences.daily_lessons_target} lesson(s) per day.

Keep up the great work!
Hebrew for Everyone
"""
    try:
        sent = send_mail(
            subject,
            body,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
    except Exception:
        logger.exception("Reminder email send raised an error for %s", user.email)
        return False
    if sent:
        from django.utils import timezone
        LearningPreferences.objects.filter(pk=preferences.pk).update(
            last_reminder_sent_at=timezone.now()
        )
        return True
    logger.warning("Reminder email was not accepted by backend for %s", user.email)
    return False