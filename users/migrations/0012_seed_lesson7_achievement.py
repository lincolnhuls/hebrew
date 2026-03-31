# Data migration: seed Lesson 7 completion achievement

from django.db import migrations


def seed_lesson7(apps, schema_editor):
    Achievement = apps.get_model("users", "Achievement")
    Achievement.objects.get_or_create(
        slug="lesson-complete-roots-1",
        defaults={
            "name": "Lesson Complete – Root Restoration",
            "description": "Finish all activities in Lesson 7.",
            "category": "lesson",
            "icon": "📖",
            "is_active": True,
        },
    )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0011_seed_lesson6_achievement"),
    ]

    operations = [
        migrations.RunPython(seed_lesson7, noop),
    ]
