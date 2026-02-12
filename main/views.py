from django.shortcuts import render, redirect

from lessons.models import Lesson, HebrewLetter
from lessons.services import get_lesson_1_combined_progress
from lessons.constants import DEFAULT_PASSES_REQUIRED


def _get_default_lesson_1_combined():
    """Return default lesson 1 combined progress structure."""
    default_alphabet = {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    return {
        "progress_pct": 0,
        "is_complete": False,
        "alphabet_1": default_alphabet.copy(),
        "alphabet_2": default_alphabet.copy(),
    }


def _get_lesson_1_combined_progress_safe(user_id):
    """Get lesson 1 combined progress with fallback to defaults."""
    try:
        return get_lesson_1_combined_progress(user_id)
    except Exception:
        return _get_default_lesson_1_combined()


def home(request):
    if request.session.get('firebase_uid'):
        return redirect('main:dashboard')
    return render(request, "main/home.html")

def dashboard(request): 
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")

    lesson_1_combined = _get_lesson_1_combined_progress_safe(login)

    return render(request, "main/dashboard.html", {
        "lesson_1_combined": lesson_1_combined,
        "lesson_1_complete": lesson_1_combined["is_complete"],
    })


def settings_page(request):
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")
    return render(request, "main/settings.html")


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

    return render(request, "main/lesson_runner.html", {
        "lesson_slug": lesson_slug,
        "lesson_title": lesson.title,
        "user_id": firebase_uid,
    })


def lesson_1_hub(request):
    """Lesson 1 hub: Learn the alphabet, Letters 1-11, Letters 12-22."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    combined = _get_lesson_1_combined_progress_safe(firebase_uid)

    return render(request, "main/lesson_1_hub.html", {
        "lesson_1_combined": combined,
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


def lesson_2_hub(request):
    """Lesson 2 hub: Learn Special Letters (similar, begadkefat, final) + quizzes (placeholders)."""
    firebase_uid = request.session.get('firebase_uid')
    if not firebase_uid:
        return redirect('users:account')

    return render(request, "main/lesson_2_hub.html", {})


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