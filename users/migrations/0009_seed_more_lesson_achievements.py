# Data migration: seed additional lesson completion achievements

from django.db import migrations


def seed_more(apps, schema_editor):
    Achievement = apps.get_model("users", "Achievement")
    rows = [
        (
            "lesson-complete-vowels-1",
            "Lesson Complete – Vowels",
            "Finish all activities in Lesson 3.",
            "lesson",
            "📖",
        ),
        (
            "lesson-complete-aspect-1",
            "Lesson Complete – Aspect",
            "Finish all activities in Lesson 4.",
            "lesson",
            "📖",
        ),
    ]
    for slug, name, description, category, icon in rows:
        Achievement.objects.get_or_create(
            slug=slug,
            defaults={
                "name": name,
                "description": description,
                "category": category,
                "icon": icon,
                "is_active": True,
            },
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("users", "0008_seed_achievements"),
    ]

    operations = [
        migrations.RunPython(seed_more, noop),
    ]

