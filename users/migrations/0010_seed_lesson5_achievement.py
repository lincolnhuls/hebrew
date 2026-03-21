# Data migration: seed Lesson 5 completion achievement

from django.db import migrations


def seed_lesson5(apps, schema_editor):
    Achievement = apps.get_model("users", "Achievement")
    Achievement.objects.get_or_create(
        slug="lesson-complete-suffixes-1",
        defaults={
            "name": "Lesson Complete – Pronominal Suffixes",
            "description": "Finish all activities in Lesson 5.",
            "category": "lesson",
            "icon": "📖",
            "is_active": True,
        },
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0009_seed_more_lesson_achievements"),
    ]

    operations = [
        migrations.RunPython(seed_lesson5, noop),
    ]

