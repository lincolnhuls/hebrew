from django.core.management.base import BaseCommand

from lessons.models import Lesson, LessonSession


class Command(BaseCommand):
    help = "Reset progress for a specific lesson. Deletes all LessonSession records for the given user_id and lesson_slug."

    def add_arguments(self, parser):
        parser.add_argument(
            "user_id",
            type=str,
            help="Firebase UID of the user whose progress to reset.",
        )
        parser.add_argument(
            "lesson_slug",
            type=str,
            help="Lesson slug to reset (e.g. alphabet-1, begadkefat-letters).",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be deleted without actually deleting.",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        lesson_slug = options["lesson_slug"]
        dry_run = options["dry_run"]

        try:
            lesson = Lesson.objects.get(slug=lesson_slug)
        except Lesson.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f"Lesson with slug '{lesson_slug}' not found.")
            )
            return

        sessions = LessonSession.objects.filter(user_id=user_id, lesson=lesson)
        count = sessions.count()

        if count == 0:
            self.stdout.write(
                self.style.WARNING(
                    f"No lesson sessions found for user {user_id} and lesson '{lesson_slug}'."
                )
            )
            return

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"DRY RUN: Would delete {count} lesson session(s) for user {user_id} and lesson '{lesson_slug}'."
                )
            )
            for s in sessions[:10]:
                status = "completed" if s.completed else "in progress"
                passed = "passed" if s.passed else "failed"
                self.stdout.write(f"  - {s.lesson.title} ({status}, {passed})")
            if count > 10:
                self.stdout.write(f"  ... and {count - 10} more")
            return

        deleted, _ = sessions.delete()
        self.stdout.write(
            self.style.SUCCESS(
                f"Deleted {deleted} record(s) for user {user_id} and lesson '{lesson_slug}'. Progress reset."
            )
        )
