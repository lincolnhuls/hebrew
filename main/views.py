from django.shortcuts import render, redirect
from django.http import HttpResponse

from lessons.models import Lesson, HebrewLetter
from lessons.services import get_user_lesson_progress, get_lesson_1_combined_progress


def home(request):
    if request.session.get('firebase_uid'):
        return redirect('main:dashboard')
    return render(request, "main/home.html")

def dashboard(request): 
    login = request.session.get('firebase_uid')
    if not login:
        return render(request, "users/users.html")

    default_alphabet = {"pass_count": 0, "passes_required": 4, "progress_pct": 0, "is_complete": False}
    lesson_1_combined = {
        "progress_pct": 0,
        "is_complete": False,
        "alphabet_1": default_alphabet.copy(),
        "alphabet_2": default_alphabet.copy(),
    }
    try:
        lesson_1_combined = get_lesson_1_combined_progress(login)
    except Exception:
        pass

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

    default_alphabet = {"pass_count": 0, "passes_required": 4, "progress_pct": 0, "is_complete": False}
    combined = {
        "progress_pct": 0,
        "is_complete": False,
        "alphabet_1": default_alphabet.copy(),
        "alphabet_2": default_alphabet.copy(),
    }
    try:
        combined = get_lesson_1_combined_progress(firebase_uid)
    except Exception:
        pass

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