from django.http import JsonResponse
import json
from datetime import datetime, time
from users.models import UserInformation, LearningPreferences
from users.utils import send_learning_goals_confirmation

DEFAULT_REMINDER_TIME = time(9, 0)

def learning_preferences(request):
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return JsonResponse({
            'ok': False,
            'error': 'User not authenticated',
        })
    try:
        user = UserInformation.objects.get(firebase_uid=firebase_uid)
    except UserInformation.DoesNotExist:
        return JsonResponse({
            'ok': False,
            'error': 'User not found'
        })
    if request.method == 'GET':
        try:
            preferences = LearningPreferences.objects.get(user=user)
        except LearningPreferences.DoesNotExist:
            return JsonResponse({
                'ok': True,
                'has_preferences': False
            })
        prefs_data = {
            'daily_lessons_target': preferences.daily_lessons_target,
            'reminder_enabled': preferences.reminder_enabled,
            'reminder_frequency': preferences.reminder_frequency,
            'reminder_time': preferences.reminder_time.isoformat() if preferences.reminder_time else None,
            'timezone': preferences.timezone
        }
        return JsonResponse({
            'ok': True,
            'has_preferences': True,
            'preferences': prefs_data
        })
    elif request.method == 'POST':
        try:
            data = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse(
                {"ok": False, "error": "invalid_json"},
                status=400,
            )
        raw_target = data.get("daily_lessons_target")
        try:
            daily_lessons_target = int(raw_target)
        except (TypeError, ValueError):
            return JsonResponse(
                {"ok": False, "error": "daily_lessons_target_must_be_integer"},
                status=400,
            )
        if daily_lessons_target < 1:
            return JsonResponse(
                {"ok": False, "error": "daily_lessons_target_must_be_at_least_1"},
                status=400,
            )
        raw_enabled = data.get("reminder_enabled")
        if raw_enabled is None:
            reminder_enabled = True
        elif isinstance(raw_enabled, bool):
            reminder_enabled = raw_enabled
        else:
            return JsonResponse(
                {"ok": False, "error": "reminder_enabled_must_be_boolean"},
                status=400,
            )
        raw_frequency = data.get("reminder_frequency")
        valid_frequencies = [choice[0] for choice in LearningPreferences.REMINDER_FREQUENCY_CHOICES]
        if raw_frequency not in valid_frequencies:
            return JsonResponse(
                {"ok": False, "error": "invalid_reminder_frequency"},
                status=400,
            )
        raw_time = data.get("reminder_time")
        if raw_time:
            try:
                reminder_time = datetime.strptime(raw_time, "%H:%M").time()
            except ValueError:
                return JsonResponse(
                    {"ok": False, "error": "reminder_time_must_be_HH_MM"},
                    status=400,
                )
        else:
            # If not set, default to 9:00 AM in the user's selected timezone.
            reminder_time = DEFAULT_REMINDER_TIME
        timezone = data.get("timezone") or "UTC"
        prefs, _created = LearningPreferences.objects.update_or_create(
            user=user,
            defaults={
                "daily_lessons_target": daily_lessons_target,
                "reminder_enabled": reminder_enabled,
                "reminder_frequency": raw_frequency,
                "reminder_time": reminder_time,
                "timezone": timezone,
            },
        )
        send_learning_goals_confirmation(user, prefs)
        prefs_data = {
            "daily_lessons_target": prefs.daily_lessons_target,
            "reminder_enabled": prefs.reminder_enabled,
            "reminder_frequency": prefs.reminder_frequency,
            "reminder_time": prefs.reminder_time.isoformat() if prefs.reminder_time else None,
            "timezone": prefs.timezone,
        }
        return JsonResponse(
            {
                "ok": True,
                "has_preferences": True,
                "preferences": prefs_data,
            }
        )

    else:
        return JsonResponse({
            'ok': False,
            'error': 'Invalid request method'
        })
    

