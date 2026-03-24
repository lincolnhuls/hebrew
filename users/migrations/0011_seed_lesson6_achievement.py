# Data migration: seed Lesson 6 completion achievement

from django.db import migrations


def seed_lesson6(apps, schema_editor):
    Achievement = apps.get_model("users", "Achievement")
    Achievement.objects.get_or_create(
        slug="lesson-complete-prepositions-1",
        defaults={
            "name": "Lesson Complete – Prepositions",
            "description": "Finish all activities in Lesson 6.",
            "category": "lesson",
            "icon": "📖",
            "is_active": True,
        },
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0010_seed_lesson5_achievement"),
    ]

    operations = [
        migrations.RunPython(seed_lesson6, noop),
    ]

