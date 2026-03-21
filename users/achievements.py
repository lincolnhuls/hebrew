from django.utils import timezone
from .models import UserInformation, Achievement, UserAchievement

FAST_LEARNER_MINUTES = 5

def award_achievement(user: UserInformation, slug: str) -> bool:
    try:
        achievement = Achievement.objects.get(slug=slug, is_active=True)
    except Achievement.DoesNotExist:
        return False
    _, created = UserAchievement.objects.get_or_create(user=user, achievement=achievement)
    return created

def check_lesson_achievements(user: UserInformation, lesson, session) -> None:
    if not session.completed or not session.passed:
        return
    slug = getattr(lesson, "slug", None)
    if not slug:
        return
    
    if slug == "alphabet-1":
        award_achievement(user, "lesson-complete-alphabet-1")
    elif slug == "alphabet-2":
        award_achievement(user, "lesson-complete-alphabet-2")
    elif slug == "vowels-1":
        award_achievement(user, "lesson-complete-vowels-1")
    elif slug == "aspect-1":
        award_achievement(user, "lesson-complete-aspect-1")
    elif slug == "suffixes-1":
        award_achievement(user, "lesson-complete-suffixes-1")
        
    from lessons.models import LessonAnswer
    total = LessonAnswer.objects.filter(session=session).values("question_index").distinct().count()
    correct = LessonAnswer.objects.filter(session=session, correct=True).values("question_index").distinct().count()
    if total > 0 and correct >= total:
        if slug == "alphabet-1":
            award_achievement(user, "perfect-score-alphabet-1")
        elif slug == "alphabet-2":
            award_achievement(user, "perfect-score-alphabet-2")
            
    if getattr(session, "started_at", None) and getattr(session, "completed_at", None):
        delta = session.completed_at - session.started_at
        if delta.total_seconds() < FAST_LEARNER_MINUTES * 60:
            award_achievement(user, "fast-learner")
            
def check_answer_achievements(user: UserInformation) -> None:
    if user.total_answers >= 500:
        award_achievement(user, "answers-500")
    if user.total_correct_answers >= 50:
        award_achievement(user, "reading-rookie")
    if user.total_correct_answers >= 500:
        award_achievement(user, "reading-pro")
        

def update_streaks_and_award(user: UserInformation, today_lesson_count: int) -> None:
    today = timezone.now().date()
    daily_target = 1
    try:
        prefs = getattr(user, "learning_preferences", None)
        if prefs is not None and prefs.daily_lessons_target > 0:
            daily_target = prefs.daily_lessons_target
    except Exception:
        pass
    
    goal_met_today = today_lesson_count >= daily_target
    
    last_activity = user.last_activity_date
    if last_activity is None:
        user.current_activity_streak_days = 1
    elif last_activity == today:
        pass
    elif (today - last_activity).days == 1:
        user.current_activity_streak_days = (user.current_activity_streak_days or 0) + 1
    else:
        user.current_activity_streak_days = 1
    user.last_activity_date = today
    
    last_goal = user.last_goal_met_date
    if goal_met_today:
        if last_goal is None:
            user.current_goal_streak_days = 1
        elif last_goal == today:
            pass
        elif (today - last_goal).days == 1:
            user.current_goal_streak_days = (user.current_goal_streak_days or 0) + 1
        else:
            user.current_goal_streak_days = 1
        user.last_goal_met_date = today
    else:
        user.current_goal_streak_days = 0
        
    user.save(update_fields=[
        "last_activity_date", "current_activity_streak_days",
        "last_goal_met_date", "current_goal_streak_days",
    ])
    
    if (user.current_activity_streak_days or 0) >= 7:
        award_achievement(user, "streak-7-days")
    if (user.current_goal_streak_days or 0) >= 7:
        award_achievement(user, "goal-week")
    if (user.current_goal_streak_days or 0) >= 30:
        award_achievement(user, "goal-streak-30")
    