from django.core.management.base import BaseCommand
from django.utils import timezone

from lessons.models import Lesson, LessonSession


class Command(BaseCommand):
    help = "Fill lesson progress for a user. Creates completed, passed LessonSession records to meet passes_required."

    def add_arguments(self, parser):
        parser.add_argument(
            "user_id",
            type=str,
            help="Firebase UID of the user whose progress to fill.",
        )
        parser.add_argument(
            "--lesson",
            type=str,
            help="Lesson slug to fill (e.g. alphabet-1, alphabet-2). If omitted, fills all lessons.",
        )
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help="Show what would be created without actually creating.",
        )

    def handle(self, *args, **options):
        user_id = options["user_id"]
        lesson_slug = options.get("lesson")
        dry_run = options["dry_run"]

        if lesson_slug:
            lessons = Lesson.objects.filter(slug=lesson_slug)
            if not lessons.exists():
                self.stdout.write(
                    self.style.ERROR(f"Lesson with slug '{lesson_slug}' not found.")
                )
                return
        else:
            lessons = Lesson.objects.all().order_by("order")

        created_total = 0
        for lesson in lessons:
            current_pass_count = LessonSession.objects.filter(
                user_id=user_id,
                lesson=lesson,
                completed=True,
                passed=True,
            ).count()
            required = lesson.passes_required
            to_create = max(0, required - current_pass_count)

            if to_create == 0:
                self.stdout.write(
                    f"  {lesson.slug}: already complete ({current_pass_count}/{required} passes)"
                )
                continue

            if dry_run:
                self.stdout.write(
                    self.style.WARNING(
                        f"  {lesson.slug}: would create {to_create} session(s) "
                        f"({current_pass_count}/{required} → {required}/{required})"
                    )
                )
                created_total += to_create
                continue

            for _ in range(to_create):
                LessonSession.objects.create(
                    user_id=user_id,
                    lesson=lesson,
                    question_set_json=[],
                    current_index=0,
                    completed=True,
                    completed_at=timezone.now(),
                    passed=True,
                )
                created_total += 1

            self.stdout.write(
                self.style.SUCCESS(
                    f"  {lesson.slug}: created {to_create} session(s) "
                    f"({current_pass_count} → {required} passes)"
                )
            )

        if dry_run:
            self.stdout.write(
                self.style.WARNING(
                    f"\nDRY RUN: Would create {created_total} total session(s) for user {user_id}."
                )
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    f"\nCreated {created_total} session(s) for user {user_id}. Progress filled."
                )
            )
