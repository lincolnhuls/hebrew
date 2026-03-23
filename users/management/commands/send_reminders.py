from zoneinfo import ZoneInfo
from datetime import time

from django.core.management.base import BaseCommand
from django.utils import timezone

from users.models import LearningPreferences
from users.utils import send_reminder_email

DEFAULT_REMINDER_TIME = time(9, 0)
WEEKLY_REMINDER_WEEKDAY = 0  # Monday

class Command(BaseCommand):
    help = 'Send study reminder emails to users based on their preferences and timezone'
    
    def add_arguments(self, parser):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show who would receive reminders without sending",
        )
        
    def handle(self, *args, **options):
        dry_run = options["dry_run"]
        now_utc = timezone.now()
        
        prefs = LearningPreferences.objects.filter(
            reminder_enabled=True,
        ).select_related("user")
        
        sent_count = 0
        for prefs_obj in prefs:
            user = prefs_obj.user
            if not user.email:
                continue
            
            try:
                tz = ZoneInfo(prefs_obj.timezone)
            except Exception:
                tz = ZoneInfo("UTC")
                
            local_now = now_utc.astimezone(tz)
            local_date = local_now.date()
            local_time = local_now.time()
            reminder_time = prefs_obj.reminder_time or DEFAULT_REMINDER_TIME
            
            if local_time.hour != reminder_time.hour:
                continue
            
            last_sent = prefs_obj.last_reminder_sent_at
            if last_sent:
                last_sent_local = last_sent.astimezone(tz)
                last_sent_date = last_sent_local.date()
                
            if prefs_obj.reminder_frequency == LearningPreferences.DAILY:
                if last_sent and last_sent_date >= local_date:
                    continue
            elif prefs_obj.reminder_frequency == LearningPreferences.WEEKDAYS:
                if local_date.weekday() >= 5:
                    continue
                if last_sent and last_sent_date >= local_date:
                    continue
            elif prefs_obj.reminder_frequency == LearningPreferences.WEEKLY:
                # Weekly reminders are sent on Monday only.
                if local_date.weekday() != WEEKLY_REMINDER_WEEKDAY:
                    continue
                # Avoid duplicate sends the same day.
                if last_sent and last_sent_date >= local_date:
                    continue
                
            if dry_run:
                self.stdout.write(
                    self.style.WARNING(f"Would send reminder to {user.email}")
                )
            else:
                if send_reminder_email(user, prefs_obj):
                    sent_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Sent reminder to {user.email}")
                    )
        if dry_run:
            self.stdout.write(self.style.WARNING(f'\nDry run complete. No emails sent.'))
        else:
            self.stdout.write(
                self.style.SUCCESS(f'\nSent {sent_count} reminder(s)')
            )
