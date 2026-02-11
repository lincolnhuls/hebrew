from lessons.models import Lesson, LessonSession, HebrewLetter, LessonAnswer
from lessons.generators import generate_alphabet_1_questions, generate_alphabet_2_questions
from lessons.constants import (
    RANDOM_SEED_MIN, RANDOM_SEED_MAX,
    ALPHABET_1_START, ALPHABET_1_END,
    ALPHABET_2_START, ALPHABET_2_END,
    PASS_THRESHOLD
)
from django.utils import timezone
from django.core.exceptions import ValidationError
from random import Random

def start_lesson_session(user_id: str, lesson_slug: str) -> LessonSession:
    """Start a new lesson session for a user.
    
    Args:
        user_id: Firebase UID of the user
        lesson_slug: Slug identifier for the lesson (e.g., 'alphabet-1', 'alphabet-2')
    
    Returns:
        Created LessonSession instance with generated question set
    
    Raises:
        Lesson.DoesNotExist: If lesson with given slug doesn't exist
        ValidationError: If lesson_slug format is invalid
    """
    # Validate lesson_slug format (basic validation)
    if not lesson_slug or not isinstance(lesson_slug, str):
        raise ValidationError("Invalid lesson_slug format")
    
    # Validate user_id format (basic validation)
    if not user_id or not isinstance(user_id, str):
        raise ValidationError("Invalid user_id format")
    
    try:
        lesson = Lesson.objects.get(slug=lesson_slug)
    except Lesson.DoesNotExist:
        raise Lesson.DoesNotExist(f"Lesson with slug '{lesson_slug}' does not exist")
    
    seed = Random().randint(RANDOM_SEED_MIN, RANDOM_SEED_MAX)
    session = LessonSession.objects.create(
        user_id=user_id,
        lesson=lesson,
        seed=seed
    )

    if lesson_slug == "alphabet-2":
        letters = list(
            HebrewLetter.objects
            .filter(order__gte=ALPHABET_2_START, order__lte=ALPHABET_2_END)
            .order_by("order")
            .values("letter", "name_en")
        )
        questions = generate_alphabet_2_questions(letters, session.seed)
    else:
        letters = list(
            HebrewLetter.objects
            .filter(order__gte=ALPHABET_1_START, order__lte=ALPHABET_1_END)
            .order_by("order")
            .values("letter", "name_en")
        )
        questions = generate_alphabet_1_questions(letters, session.seed)
    
    # Validate question set was generated
    if not questions or len(questions) == 0:
        raise ValueError("Failed to generate question set for lesson")

    session.question_set_json = questions
    session.save(update_fields=["question_set_json"])
    return session

def submit_answer(session_id: int, question_index: int, user_answer_json: dict, user_id: str = None) -> dict:
    """Submit an answer for a question in a lesson session.
    
    Args:
        session_id: ID of the lesson session
        question_index: Index of the question being answered
        user_answer_json: User's answer as a dictionary
        user_id: Optional user_id to validate session ownership (security check)
    
    Returns:
        Dictionary with 'correct', 'completed', and 'current_index' keys
    
    Raises:
        LessonSession.DoesNotExist: If session doesn't exist
        ValueError: If session is completed, question_index is invalid, or user_id doesn't match
        IndexError: If question_index is out of bounds
    """
    try:
        session = LessonSession.objects.select_related('lesson').get(id=session_id)
    except LessonSession.DoesNotExist:
        raise LessonSession.DoesNotExist(f"Session with id {session_id} does not exist")
    
    # Security: Validate session ownership if user_id provided
    if user_id and session.user_id != user_id:
        raise ValueError("Session does not belong to this user")
    
    if session.completed:
        raise ValueError("Session already completed")
    
    questions = session.question_set_json or []
    if not questions:
        raise ValueError("Session has no questions")
    
    if question_index < 0 or question_index >= len(questions):
        raise IndexError(f"Invalid question index: {question_index} (valid range: 0-{len(questions)-1})")
    
    try:
        question = questions[question_index]
    except (IndexError, TypeError) as e:
        raise IndexError(f"Invalid question index: {question_index}") from e
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
        # Compute pass: >= PASS_THRESHOLD correct (distinct questions)
        correct_count = (
            LessonAnswer.objects
            .filter(session=session, correct=True)
            .values("question_index")
            .distinct()
            .count()
        )
        session.passed = correct_count >= PASS_THRESHOLD
    
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


def get_user_lesson_progress(user_id: str, lesson_slug: str) -> dict | None:
    """Returns progress for a user on a lesson (Duolingo-style: N passes required).
    
    Args:
        user_id: Firebase UID of the user
        lesson_slug: Slug identifier for the lesson
    
    Returns:
        Dictionary with pass_count, passes_required, progress_pct (0-100), is_complete (bool),
        or None if lesson doesn't exist
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


def get_lesson_1_combined_progress(user_id: str) -> dict:
    """Get combined progress for Lesson 1 (alphabet-1 + alphabet-2).
    
    Lesson 1 combines alphabet-1 and alphabet-2. Each contributes 50% to the total.
    Lesson 1 is complete when BOTH alphabet-1 and alphabet-2 have DEFAULT_PASSES_REQUIRED passes each.
    
    Args:
        user_id: Firebase UID of the user
    
    Returns:
        Dictionary with progress_pct (0-100), is_complete (bool), alphabet_1, alphabet_2
    """
    from lessons.constants import LESSON_1_COMBINED_WEIGHT, DEFAULT_PASSES_REQUIRED
    
    p1 = get_user_lesson_progress(user_id, "alphabet-1")
    p2 = get_user_lesson_progress(user_id, "alphabet-2")
    alphabet_1 = p1 if p1 else {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    alphabet_2 = p2 if p2 else {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    # Each half contributes 50%
    combined_pct = (alphabet_1["progress_pct"] * LESSON_1_COMBINED_WEIGHT) + (alphabet_2["progress_pct"] * LESSON_1_COMBINED_WEIGHT)
    is_complete = alphabet_1["is_complete"] and alphabet_2["is_complete"]
    return {
        "progress_pct": min(100, int(combined_pct)),
        "is_complete": is_complete,
        "alphabet_1": alphabet_1,
        "alphabet_2": alphabet_2,
    }