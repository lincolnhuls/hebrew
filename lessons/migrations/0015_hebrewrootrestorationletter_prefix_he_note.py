# Disambiguate prefix ה chart row (same letter also appears as suffix in another row).

from django.db import migrations


def set_prefix_he_note(apps, schema_editor):
    HebrewRootRestorationLetter = apps.get_model("lessons", "HebrewRootRestorationLetter")
    row = HebrewRootRestorationLetter.objects.filter(
        order=1, letter="ה", slot="prefix"
    ).first()
    if row and not (row.notes or "").strip():
        row.notes = "before _ _"
        row.save(update_fields=["notes"])


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0014_hebrewrootrestorationletter_and_lesson7"),
    ]

    operations = [
        migrations.RunPython(set_prefix_he_note, noop),
    ]
