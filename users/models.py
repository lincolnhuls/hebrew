from django.db import models
    
class UserInformation(models.Model):
    firebase_uid = models.CharField(max_length=200, unique=True, db_index=True)
    name = models.CharField(max_length=50)
    email = models.EmailField(max_length=254, db_index=True)

    total_answers = models.PositiveIntegerField(default=0)
    total_correct_answers = models.PositiveIntegerField(default=0)
    current_goal_streak_days = models.PositiveIntegerField(default=0)
    current_activity_streak_days = models.PositiveIntegerField(default=0)
    last_activity_date = models.DateField(null=True, blank=True)
    last_goal_met_date = models.DateField(null=True, blank=True)
    
    class Meta:
        verbose_name = "User Information"
        verbose_name_plural = "User Information"
        ordering = ["name"]
    
    def __str__(self):
        return self.name

class LearningPreferences(models.Model):
    DAILY = "daily"
    WEEKDAYS = "weekdays"
    WEEKLY = "weekly"

    REMINDER_FREQUENCY_CHOICES = [
        (DAILY, "Every Day"),
        (WEEKDAYS, "Weekdays"),
        (WEEKLY, "Once a Week")
    ]

    user = models.OneToOneField(
        UserInformation,
        on_delete=models.CASCADE,
        related_name="learning_preferences",
    )

    daily_lessons_target = models.PositiveSmallIntegerField(default=1)

    reminder_enabled = models.BooleanField(default=True)
    reminder_frequency = models.CharField(
        max_length=16,
        choices=REMINDER_FREQUENCY_CHOICES,
        default=WEEKLY,
    )
    reminder_time = models.TimeField(null=True, blank=True)
    timezone = models.CharField(max_length=64, default="UTC")

    last_reminder_sent_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Learning Preferences for {self.user.name or self.user.email}"

class Achievement(models.Model):
    slug = models.SlugField(max_length=64, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    category = models.CharField(
        max_length=32,
        choices=[
            ("lesson", "Lesson"),
            ("progress", "Progress"),
            ("daily_goal", "Daily Goal"),
            ("streak", "Streak"),
            ("volume", "Volume"),
        ],
    )
    icon = models.CharField(max_length=8, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class UserAchievement(models.Model):
    user = models.ForeignKey(UserInformation, on_delete=models.CASCADE, related_name="achievements")
    achievement = models.ForeignKey(Achievement, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [("user", "achievement")]

    def __str__(self):
        return f"{self.user} → {self.achievement}"