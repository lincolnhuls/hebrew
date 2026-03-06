from django.core.management.base import BaseCommand

from users.models import UserInformation, LearningPreferences


class Command(BaseCommand):
    help = "Clear learning preferences, optionally for a single user"

    def add_arguments(self, parser):
        parser.add_argument(
            "--email",
            type=str,
            help=(
                "Email of the user whose learning preferences should be cleared. "
                "If omitted, clears all LearningPreferences rows."
            ),
        )

    def handle(self, *args, **options):
        email = options.get("email")

        if email:
            try:
                user = UserInformation.objects.get(email=email)
            except UserInformation.DoesNotExist:
                self.stderr.write(self.style.ERROR(f"No user found with email {email}"))
                return

            deleted, _ = LearningPreferences.objects.filter(user=user).delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted} LearningPreferences row(s) for {email}"
                )
            )
        else:
            deleted, _ = LearningPreferences.objects.all().delete()
            self.stdout.write(
                self.style.SUCCESS(
                    f"Deleted {deleted} LearningPreferences row(s) (all users)"
                )
            )

