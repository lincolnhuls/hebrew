# Generated: Lesson 7 root restoration (missing letter positions)

from django.db import migrations, models


def seed_roots_lesson(apps, schema_editor):
    Lesson = apps.get_model("lessons", "Lesson")
    HebrewRootRestorationLetter = apps.get_model("lessons", "HebrewRootRestorationLetter")

    Lesson.objects.update_or_create(
        slug="roots-1",
        defaults={"title": "Lesson 7: Root Restoration", "order": 7, "passes_required": 4},
    )

    rows = [
        # order, letter, slot, notes (notes disambiguate duplicate letters in quizzes)
        (1, "ה", "prefix", ""),
        (2, "ו", "prefix", "before _ _"),
        (3, "י", "middle", "between _ _"),
        (4, "ו", "middle", "between _ _"),
        (5, "י", "suffix", "after _ _"),
        (6, "נ", "suffix", ""),
        (7, "ה", "suffix", "Only with הלך"),
        (8, "ל", "suffix", "Only with לקח"),
    ]

    for order, letter, slot, notes in rows:
        HebrewRootRestorationLetter.objects.update_or_create(
            order=order,
            defaults={
                "letter": letter,
                "slot": slot,
                "notes": notes,
            },
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0013_hebrewpreposition_and_lesson6"),
    ]

    operations = [
        migrations.CreateModel(
            name="HebrewRootRestorationLetter",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("order", models.PositiveSmallIntegerField(unique=True)),
                ("letter", models.CharField(max_length=8)),
                ("slot", models.CharField(choices=[("prefix", "Prefix"), ("middle", "Middle"), ("suffix", "Suffix")], max_length=16)),
                ("notes", models.CharField(blank=True, default="", max_length=120)),
            ],
            options={
                "verbose_name": "Hebrew Root Restoration Letter",
                "verbose_name_plural": "Hebrew Root Restoration Letters",
                "ordering": ["order"],
            },
        ),
        migrations.RunPython(seed_roots_lesson, noop),
    ]
