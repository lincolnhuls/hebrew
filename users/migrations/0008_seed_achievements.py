# Data migration: seed MVP achievements

from django.db import migrations


def seed_achievements(apps, schema_editor):
    Achievement = apps.get_model("users", "Achievement")
    rows = [
        ("lesson-complete-alphabet-1", "Lesson Complete – Alphabet 1", "Finish all activities in Lesson 1.", "lesson", "📖"),
        ("lesson-complete-alphabet-2", "Lesson Complete – Alphabet 2", "Finish all activities in Lesson 2.", "lesson", "📖"),
        ("perfect-score-alphabet-1", "Perfect Score – Alphabet 1", "Pass Alphabet 1 with every answer correct.", "lesson", "⭐"),
        ("perfect-score-alphabet-2", "Perfect Score – Alphabet 2", "Pass Alphabet 2 with every answer correct.", "lesson", "⭐"),
        ("fast-learner", "Fast Learner", "Complete a lesson in under 5 minutes.", "lesson", "⚡"),
        ("reading-rookie", "Reading Rookie", "Answer 50 questions correctly.", "progress", "📚"),
        ("reading-pro", "Reading Pro", "Answer 500 questions correctly.", "progress", "📚"),
        ("goal-week", "Goal Week", "Hit your daily lesson target 7 days in a row.", "daily_goal", "🎯"),
        ("goal-streak-30", "Goal Streak – 30 Days", "Hit your daily lesson target 30 days in a row.", "daily_goal", "🏆"),
        ("streak-7-days", "7-Day Streak", "Study 7 days in a row.", "streak", "🔥"),
        ("answers-500", "500 Answers", "Answer 500 questions.", "volume", "💪"),
    ]
    for slug, name, description, category, icon in rows:
        Achievement.objects.get_or_create(
            slug=slug,
            defaults={"name": name, "description": description, "category": category, "icon": icon, "is_active": True},
        )


def noop(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ("users", "0007_achievement_and_more"),
    ]

    operations = [
        migrations.RunPython(seed_achievements, noop),
    ]
