# Migration: add passes_required to Lesson, passed to LessonSession

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("lessons", "0006_create_alphabet_1_lesson"),
    ]

    operations = [
        migrations.AddField(
            model_name="lesson",
            name="passes_required",
            field=models.PositiveSmallIntegerField(default=4),
        ),
        migrations.AddField(
            model_name="lessonsession",
            name="passed",
            field=models.BooleanField(default=False),
        ),
    ]
