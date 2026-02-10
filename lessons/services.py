from lessons.models import Lesson, LessonSession, HebrewLetter, LessonAnswer
from lessons.generators import generate_alphabet_1_questions, generate_alphabet_2_questions
from django.utils import timezone
from random import Random

def start_lesson_session(user_id, lesson_slug):
# 1) create LessonSession (store seed)
# 2) load letters for this lesson
# 3) generate question set using session.seed
# 4) save question_set_json back onto the session

    lesson = Lesson.objects.get(slug=lesson_slug)
    seed = Random().randint(1, 500_000)
    session = LessonSession.objects.create(
        user_id=user_id,
        lesson=lesson,
        seed=seed
    )

    if lesson_slug == "alphabet-2":
        letters = list(
            HebrewLetter.objects
            .filter(order__gte=12, order__lte=22)
            .order_by("order")
            .values("letter", "name_en")
        )
        questions = generate_alphabet_2_questions(letters, session.seed)
    else:
        letters = list(
            HebrewLetter.objects
            .filter(order__gte=1, order__lte=11)
            .order_by("order")
            .values("letter", "name_en")
        )
        questions = generate_alphabet_1_questions(letters, session.seed)

    session.question_set_json = questions
    session.save(update_fields=["question_set_json"])
    return session

def submit_answer(session_id, question_index, user_answer_json):
    session = LessonSession.objects.get(id=session_id)
    
    if session.completed:
        raise ValueError("Session already completed")
    
    questions = session.question_set_json or []
    if question_index < 0 or question_index >= len(questions):
        raise ValueError("Invalid question index")
    
    question = questions[question_index]
    correct = check_correctness(question, user_answer_json)
    
    LessonAnswer.objects.create(
        session=session,
        question_index=question_index,
        user_answer_json=user_answer_json,
        correct=correct,
        answered_at=timezone.now()
    )
    
    session.current_index = max(session.current_index or 0, question_index + 1)
    
    if session.current_index >= len(questions):
        session.completed = True
        session.completed_at = timezone.now()
        # Compute pass: >= 12 correct (distinct questions)
        correct_count = (
            LessonAnswer.objects
            .filter(session=session, correct=True)
            .values("question_index")
            .distinct()
            .count()
        )
        session.passed = correct_count >= 12
    
    update_fields = ["current_index", "completed", "completed_at"]
    if session.completed:
        update_fields.append("passed")
    session.save(update_fields=update_fields)
    
    return {
        "correct": correct,
        "completed": session.completed,
        "current_index": session.current_index
    }
    
def _norm(s: str) -> str:
    return (s or "").strip().lower()

def check_correctness(question: dict, user_answer: dict) -> bool:
    qtype = question.get("type")
    
    if qtype == "mc":
        return user_answer.get("choice") == question.get("answer")
    
    if qtype == "fill":
        return _norm(user_answer.get("answer")) == _norm(question.get("answer"))
    
    if qtype == "match":
        user_pairs = user_answer.get("pairs") or []
        correct_pairs = question.get("pairs") or []
        
        if len(user_pairs) != len(correct_pairs):
            return False
        
        def canon(pairs):
            return sorted(
                [(p.get("left"), _norm(p.get("right"))) for p in pairs],
                key=lambda t: t[0] or ""
            )
        
        return canon(user_pairs) == canon(correct_pairs)
    
    raise ValueError(f"Unknown question type: {qtype}")


def get_user_lesson_progress(user_id, lesson_slug):
    """
    Returns progress for a user on a lesson (Duolingo-style: N passes required).
    Returns: dict with pass_count, passes_required, progress_pct (0-100), is_complete (bool)
    """
    try:
        lesson = Lesson.objects.get(slug=lesson_slug)
    except Lesson.DoesNotExist:
        return None

    pass_count = (
        LessonSession.objects
        .filter(user_id=user_id, lesson=lesson, completed=True, passed=True)
        .count()
    )
    required = lesson.passes_required
    progress_pct = min(100, int((pass_count / required) * 100)) if required else 0
    is_complete = pass_count >= required

    return {
        "pass_count": pass_count,
        "passes_required": required,
        "progress_pct": progress_pct,
        "is_complete": is_complete,
    }


def get_lesson_1_combined_progress(user_id):
    """
    Lesson 1 combines alphabet-1 and alphabet-2. Each contributes 50% to the total.
    Lesson 1 is complete when BOTH alphabet-1 and alphabet-2 have 4 passes each.
    Returns: dict with progress_pct (0-100), is_complete (bool), alphabet_1, alphabet_2
    """
    p1 = get_user_lesson_progress(user_id, "alphabet-1")
    p2 = get_user_lesson_progress(user_id, "alphabet-2")
    alphabet_1 = p1 if p1 else {"pass_count": 0, "passes_required": 4, "progress_pct": 0, "is_complete": False}
    alphabet_2 = p2 if p2 else {"pass_count": 0, "passes_required": 4, "progress_pct": 0, "is_complete": False}
    # Each half contributes 50%
    combined_pct = (alphabet_1["progress_pct"] * 0.5) + (alphabet_2["progress_pct"] * 0.5)
    is_complete = alphabet_1["is_complete"] and alphabet_2["is_complete"]
    return {
        "progress_pct": min(100, int(combined_pct)),
        "is_complete": is_complete,
        "alphabet_1": alphabet_1,
        "alphabet_2": alphabet_2,
    }