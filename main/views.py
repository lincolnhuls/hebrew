from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from lessons.models import Lesson, HebrewLetter, LessonSession
from lessons.services import review_items, get_lesson_1_combined_progress, get_lesson_2_combined_progress
from lessons.constants import DEFAULT_PASSES_REQUIRED
from django.utils import timezone
from users.models import UserInformation, Achievement, UserAchievement
from users.achievements import update_streaks_and_award, award_achievement

def ping(request):
    return HttpResponse("ok")

def _get_default_lesson_1_combined():
    """Return default lesson 1 combined progress structure."""
    default_alphabet = {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    return {
        "progress_pct": 0,
        "is_complete": False,
        "alphabet_1": default_alphabet.copy(),
        "alphabet_2": default_alphabet.copy(),
    }
    
    
def _get_default_lesson_2_combined():
    """Return default lesson 2 combined progress structure."""
    default_sublesson = {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    return {
        "progress_pct": 0,
        "is_complete": False,
        "similar_letters": default_sublesson.copy(),
        "begadkefat_letters": default_sublesson.copy(),
        "final_letters": default_sublesson.copy()
    }


def _get_lesson_1_combined_progress_safe(user_id):
    """Get lesson 1 combined progress with fallback to defaults."""
    try:
        return get_lesson_1_combined_progress(user_id)
    except Exception:
        return _get_default_lesson_1_combined()


def _get_lesson_2_combined_progress_safe(user_id):
    """Get lesson 2 combined progress with fallback to defaults."""
    try:
        return get_lesson_2_combined_progress(user_id)
    except Exception:
        return _get_default_lesson_2_combined()

def home(request):
    if request.session.get('firebase_uid'):
        return redirect('main:dashboard')
    return render(request, "main/home.html")


def dashboard(request):
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return render(request, "users/users.html")

    lesson_1_combined = _get_lesson_1_combined_progress_safe(firebase_uid)
    lesson_2_combined = _get_lesson_2_combined_progress_safe(firebase_uid)

    daily_target = 1
    today_completed = 0

    try:
        user = UserInformation.objects.get(firebase_uid=firebase_uid)
        prefs = getattr(user, "learning_preferences", None)
        if prefs is not None and prefs.daily_lessons_target > 0:
            daily_target = prefs.daily_lessons_target
    except UserInformation.DoesNotExist:
        user = None
        prefs = None

    today = timezone.now().date()
    today_completed = LessonSession.objects.filter(
        user_id=firebase_uid,
        completed=True,
        passed=True,
        completed_at__date=today,
    ).count()

    if daily_target > 0:
        today_goal_percent = int(min(100, round(100 * today_completed / daily_target)))
    else:
        today_goal_percent = 0

    if user:
        update_streaks_and_award(user, today_completed)
        if lesson_1_combined["is_complete"]:
            award_achievement(user, "lesson-complete-alphabet-1")
        if lesson_2_combined["is_complete"]:
            award_achievement(user, "lesson-complete-alphabet-2")
    streak_days = user.current_activity_streak_days if user else 0

    level = 2 if lesson_2_combined["is_complete"] else (1 if lesson_1_combined["is_complete"] else 0)

    passed_sessions = LessonSession.objects.filter(
        user_id=firebase_uid, completed=True, passed=True
    )
    regular_passes = passed_sessions.filter(seed__isnull=False).count()
    review_passes = passed_sessions.filter(seed__isnull=True).count()
    total_xp = regular_passes * 100 + review_passes * 50

    earned_achievements = []
    if user:
        earned_achievements = list(
            UserAchievement.objects.filter(user=user)
            .select_related("achievement")
            .order_by("-earned_at")
        )

    return render(request, "main/dashboard.html", {
        "lesson_1_combined": lesson_1_combined,
        "lesson_1_complete": lesson_1_combined["is_complete"],
        "lesson_2_combined": lesson_2_combined,
        "lesson_2_complete": lesson_2_combined["is_complete"],
        "today_lessons_completed": today_completed,
        "today_lessons_target": daily_target,
        "today_goal_percent": today_goal_percent,
        "streak_days": streak_days,
        "level": level,
        "total_xp": total_xp,
        "earned_achievements": earned_achievements,
    })

def settings_page(request):
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")
    return render(request, "main/settings.html")

def achievements_page(request):
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return render(request, "users/users.html")
    
    try:
        user = UserInformation.objects.get(firebase_uid=firebase_uid)
    except UserInformation.DoesNotExist:
        return render(request, "users/users.html")
    
    earned = UserAchievement.objects.filter(user=user).select_related("achievement").order_by("-earned_at")
    all_achievements = Achievement.objects.filter(is_active=True).order_by("category", "slug")
    earned_slugs = {ua.achievement.slug for ua in earned}
    
    return render(request, "main/achievements.html", {
        "earned": earned,
        "all_achievements": all_achievements,
        "earned_slugs": earned_slugs,
    })

def profile_page(request):
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return render(request, "users/users.html")
    
    try:
        user = UserInformation.objects.get(firebase_uid=firebase_uid)
    except UserInformation.DoesNotExist:
        return render(request, "users/users.html")

    return render(request, "main/profile.html", {
        "user_info": user,
        "firebase_uid": firebase_uid,
    })

def lesson_runner(request, lesson_slug):
    """Render the single-page lesson runner UI."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    try:
        lesson = Lesson.objects.get(slug=lesson_slug)
    except Lesson.DoesNotExist:
        return render(request, "main/lesson_runner.html", {
            "lesson_slug": lesson_slug,
            "lesson_title": "Lesson",
            "user_id": firebase_uid,
            "lesson_error": "Lesson not found.",
        })

    context = {
        "lesson_slug": lesson_slug,
        "lesson_title": lesson.title,
        "user_id": firebase_uid,
    }
    session_id = request.GET.get("session_id")
    if session_id:
        context["session_id"] = session_id
    return render(request, "main/lesson_runner.html", context)


def lesson_1_hub(request):
    """Lesson 1 hub: Learn the alphabet, Letters 1-11, Letters 12-22."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    combined = _get_lesson_1_combined_progress_safe(firebase_uid)

    return render(request, "main/lesson_1_hub.html", {
        "lesson_1_combined": combined,
    })
    

def lesson_2_hub(request):
    """Lesson 2 hub: Learn Special Letters (similar, begadkefat, final) + quizzes (placeholders)."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')
    
    combined = _get_lesson_2_combined_progress_safe(firebase_uid)

    return render(request, "main/lesson_2_hub.html", {
        "lesson_2_combined": combined,
    })


def alphabet_learn(request):
    """Alphabet learning page: intro cards, letter grid, letter-by-letter sections."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    letters = list(
        HebrewLetter.objects
        .order_by('order')
        .values('order', 'letter', 'name_en')
    )

    return render(request, "main/alphabet_learn.html", {
        "letters": letters,
    })


def similar_letters(request):
    """Lesson 2: Similar Letters – main learning page with links to Begadkefat and Final Letters."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    return render(request, "main/similar_letters.html", {})


def begadkefat(request):
    """Lesson 2: Begadkefat letters – soft vs hard pronunciations."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    return render(request, "main/begadkefat.html", {})


def final_letters(request):
    """Lesson 2: Final letter forms – medial vs final."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    return render(request, "main/final_letters.html", {})

def review_lesson(request, lesson_slug):
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')
    lesson = get_object_or_404(Lesson, slug=lesson_slug)    
    items = review_items(firebase_uid, lesson_slug)
    lesson_title = lesson.title
    return render(request, 'main/review_lesson.html', {
        'review_items': items,
        'lesson_slug': lesson_slug,
        'lesson_title': lesson_title,
        'user_id': firebase_uid,
    })
    