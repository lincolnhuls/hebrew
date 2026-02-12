from django.core.management.base import BaseCommand

from lessons.models import LessonSession


class Command(BaseCommand):
    help = "Reset lesson progress for a user. Deletes all LessonSession records for the given firebase_uid."

    def add_arguments(self, parser):
        parser.add_argument(
            "user_id",
            type=str,
            help="Firebase UID of the user whose progress to reset.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting.",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        dry_run = options["dry_run"]

        sessions = LessonSession.objects.filter(user_id=user_id)
        count = sessions.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING(f"No lesson sessions found for user {user_id}.")
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} lesson session(s) for user {user_id}."
                )
            )
            for s in sessions[:10]:
                self.stdout.write(f"  - {s.lesson.title} ({'completed' if s.completed else 'in progress'})")
            if count > 10:
                self.stdout.write(f"  ... and {count - 10} more")
            return

        deleted, _ = sessions.delete()
        self.stdout.write(
            self.style.SUCCESS(f"Deleted {deleted} record(s) for user {user_id}. Progress reset.")
        )
