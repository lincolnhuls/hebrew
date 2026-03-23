from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from lessons.models import Lesson, HebrewLetter, LessonSession, HebrewVowel, HebrewAspectForm, HebrewPronominalSuffix
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

    # Lesson 3 (vowels) completion
    lesson_3_complete = False
    try:
        vowels_lesson = Lesson.objects.get(slug="vowels-1")
        lesson_3_pass_count = LessonSession.objects.filter(
            user_id=firebase_uid,
            lesson=vowels_lesson,
            completed=True,
            passed=True,
        ).count()
        if lesson_3_pass_count >= vowels_lesson.passes_required:
            lesson_3_complete = True
    except Lesson.DoesNotExist:
        lesson_3_complete = False

    if user and lesson_3_complete:
        award_achievement(user, "lesson-complete-vowels-1")

    # Lesson 4 (aspect) completion
    lesson_4_complete = False
    try:
        aspect_lesson = Lesson.objects.get(slug="aspect-1")
        lesson_4_pass_count = LessonSession.objects.filter(
            user_id=firebase_uid,
            lesson=aspect_lesson,
            completed=True,
            passed=True,
        ).count()
        if lesson_4_pass_count >= aspect_lesson.passes_required:
            lesson_4_complete = True
    except Lesson.DoesNotExist:
        lesson_4_complete = False

    if user and lesson_4_complete:
        award_achievement(user, "lesson-complete-aspect-1")

    # Lesson 5 (pronominal suffixes) completion
    lesson_5_complete = False
    try:
        suffixes_lesson = Lesson.objects.get(slug="suffixes-1")
        lesson_5_pass_count = LessonSession.objects.filter(
            user_id=firebase_uid,
            lesson=suffixes_lesson,
            completed=True,
            passed=True,
        ).count()
        if lesson_5_pass_count >= suffixes_lesson.passes_required:
            lesson_5_complete = True
    except Lesson.DoesNotExist:
        lesson_5_complete = False

    if user and lesson_5_complete:
        award_achievement(user, "lesson-complete-suffixes-1")

    # Level tracks the highest fully completed lesson.
    if lesson_5_complete:
        level = 5
    elif lesson_4_complete:
        level = 4
    elif lesson_3_complete:
        level = 3
    elif lesson_2_combined["is_complete"]:
        level = 2
    elif lesson_1_combined["is_complete"]:
        level = 1
    else:
        level = 0

    return render(request, "main/dashboard.html", {
        "lesson_1_combined": lesson_1_combined,
        "lesson_1_complete": lesson_1_combined["is_complete"],
        "lesson_2_combined": lesson_2_combined,
        "lesson_2_complete": lesson_2_combined["is_complete"],
        "lesson_3_complete": lesson_3_complete,
        "lesson_4_complete": lesson_4_complete,
        "lesson_5_complete": lesson_5_complete,
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


def vowels_learn(request):
    firebase_uid = request.session.get("firebase_uid")
    if not firebase_uid:
        return render(request, "users/users.html")

    vowels = HebrewVowel.objects.all().order_by("order")
    return render(request, "main/vowels_learn.html", {"vowels": vowels})


def aspect_learn(request):
    firebase_uid = request.session.get("firebase_uid")
    if not firebase_uid:
        return render(request, "users/users.html")

    forms = HebrewAspectForm.objects.all().order_by("order")
    return render(request, "main/aspect_learn.html", {"forms": forms})


def suffixes_learn(request):
    firebase_uid = request.session.get("firebase_uid")
    if not firebase_uid:
        return render(request, "users/users.html")

    suffixes = HebrewPronominalSuffix.objects.all().order_by("order")
    return render(request, "main/suffixes_learn.html", {"suffixes": suffixes})

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


def lesson_3_hub(request):
    """Lesson 3 hub: Learn vowels + vowels quiz."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    try:
        vowels_lesson = Lesson.objects.get(slug="vowels-1")
    except Lesson.DoesNotExist:
        return render(request, "main/lesson_3_hub.html", {
            "lesson_3_progress": None,
            "lesson_error": "Vowels lesson not found.",
        })

    pass_count = LessonSession.objects.filter(
        user_id=firebase_uid,
        lesson=vowels_lesson,
        completed=True,
        passed=True,
    ).count()
    required = vowels_lesson.passes_required
    if required > 0:
        progress_pct = int(min(100, round(100 * pass_count / required)))
    else:
        progress_pct = 0
    is_complete = pass_count >= required and required > 0

    lesson_3_progress = {
        "pass_count": pass_count,
        "passes_required": required,
        "progress_pct": progress_pct,
        "is_complete": is_complete,
    }

    return render(request, "main/lesson_3_hub.html", {
        "lesson_3_progress": lesson_3_progress,
    })


def lesson_4_hub(request):
    """Lesson 4 hub: Learn aspect + aspect quiz."""
    firebase_uid = request.session.get("firebase_uid")
    if not firebase_uid:
        return redirect("users:account")

    try:
        aspect_lesson = Lesson.objects.get(slug="aspect-1")
    except Lesson.DoesNotExist:
        return render(
            request,
            "main/lesson_4_hub.html",
            {"lesson_4_progress": None, "lesson_error": "Aspect lesson not found."},
        )

    pass_count = LessonSession.objects.filter(
        user_id=firebase_uid,
        lesson=aspect_lesson,
        completed=True,
        passed=True,
    ).count()
    required = aspect_lesson.passes_required
    if required > 0:
        progress_pct = int(min(100, round(100 * pass_count / required)))
    else:
        progress_pct = 0
    is_complete = pass_count >= required and required > 0

    lesson_4_progress = {
        "pass_count": pass_count,
        "passes_required": required,
        "progress_pct": progress_pct,
        "is_complete": is_complete,
    }

    return render(
        request,
        "main/lesson_4_hub.html",
        {"lesson_4_progress": lesson_4_progress},
    )


def lesson_5_hub(request):
    """Lesson 5 hub: Learn pronominal suffixes + suffixes quiz."""
    firebase_uid = request.session.get("firebase_uid")
    if not firebase_uid:
        return redirect("users:account")

    try:
        suffixes_lesson = Lesson.objects.get(slug="suffixes-1")
    except Lesson.DoesNotExist:
        return render(
            request,
            "main/lesson_5_hub.html",
            {"lesson_5_progress": None, "lesson_error": "Suffixes lesson not found."},
        )

    pass_count = LessonSession.objects.filter(
        user_id=firebase_uid,
        lesson=suffixes_lesson,
        completed=True,
        passed=True,
    ).count()
    required = suffixes_lesson.passes_required
    if required > 0:
        progress_pct = int(min(100, round(100 * pass_count / required)))
    else:
        progress_pct = 0
    is_complete = pass_count >= required and required > 0

    lesson_5_progress = {
        "pass_count": pass_count,
        "passes_required": required,
        "progress_pct": progress_pct,
        "is_complete": is_complete,
    }

    return render(
        request,
        "main/lesson_5_hub.html",
        {"lesson_5_progress": lesson_5_progress},
    )

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
    