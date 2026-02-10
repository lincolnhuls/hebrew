# Generated data migration: create alphabet-1 lesson

from django.db import migrations


def create_alphabet_lesson(apps, schema_editor):
    Lesson = apps.get_model("lessons", "Lesson")
    if not Lesson.objects.filter(slug="alphabet-1").exists():
        Lesson.objects.create(slug="alphabet-1", title="Lesson 1: Aleph-Bet", order=1)


def reverse_noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("lessons", "0005_lessonsession_seed_and_more"),
    ]

    operations = [
        migrations.RunPython(create_alphabet_lesson, reverse_noop),
    ]
