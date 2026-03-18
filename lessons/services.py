from lessons.models import Lesson, LessonSession, HebrewLetter, LessonAnswer, HebrewVowel, HebrewAspectForm
from lessons.generators import (
    generate_alphabet_1_questions,
    generate_alphabet_2_questions,
    generate_similar_letters_questions,
    generate_begadkefat_questions,
    generate_final_letters_questions,
    generate_vowels_1_questions,
    generate_aspect_1_questions,
)
from lessons.constants import (
    RANDOM_SEED_MIN, RANDOM_SEED_MAX,
    ALPHABET_1_START, ALPHABET_1_END,
    ALPHABET_2_START, ALPHABET_2_END,
    PASS_THRESHOLD, SIMILAR_LETTERS,
    BEGADKEFAT_LETTERS, FINAL_LETTERS,
    PASS_PERCENT
)
from django.utils import timezone
from django.core.exceptions import ValidationError
from random import Random
import logging
from math import ceil
from users.models import UserInformation
from users.achievements import check_answer_achievements, check_lesson_achievements, update_streaks_and_award

logger = logging.getLogger(__name__)

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

    elif lesson_slug == "vowels-1":
        vowels = list(
            HebrewVowel.objects
            .order_by("order")
            .values("symbol", "name_en", "transliteration")
        )
        questions = generate_vowels_1_questions(vowels, session.seed)

    elif lesson_slug == "aspect-1":
        forms = list(
            HebrewAspectForm.objects.order_by("order").values(
                "aspect",
                "person",
                "gender",
                "number",
                "prefix",
                "suffix",
                "pattern",
                "gloss",
            )
        )
        questions = generate_aspect_1_questions(forms, session.seed)

    elif lesson_slug == "similar-letters":
        similar_orders = set()
        for pair in SIMILAR_LETTERS:
            for order_num in pair:
                similar_orders.add(order_num)

        letters = list(
            HebrewLetter.objects
            .filter(order__in=similar_orders)
            .order_by("order")
            .values("order", "letter", "name_en")
        )
        
        letters_by_order = {}
        for letter in letters:
            letters_by_order[letter["order"]] = {"letter": letter["letter"], "name_en": letter["name_en"]}

        tuple_list = []
        for (a, b) in SIMILAR_LETTERS:
            if a in letters_by_order and b in letters_by_order:
                tuple_list.append([letters_by_order[a], letters_by_order[b]])

        questions = generate_similar_letters_questions(tuple_list, session.seed)

    elif lesson_slug == "begadkefat-letters":
        similar_orders = set()
        for pair in BEGADKEFAT_LETTERS:
            for order_num in pair:
                similar_orders.add(order_num)

        letters = list(
            HebrewLetter.objects
            .filter(order__in=similar_orders)
            .order_by("order")
            .values("order", "letter", "dagesh_name", "name_en")
        )
        
        letters_by_order = {}
        for letter in letters:
            letters_by_order[letter["order"]] = {"letter": letter["letter"], "dagesh_name": letter["dagesh_name"], "name_en": letter["name_en"], "order": letter["order"]}

        tuple_list = []
        for (a, b) in BEGADKEFAT_LETTERS:
            if a in letters_by_order and b in letters_by_order:
                tuple_list.append([letters_by_order[a], letters_by_order[b]])

        questions = generate_begadkefat_questions(tuple_list, session.seed)
        
    elif lesson_slug == "final-letters":
        similar_orders = set()
        for pair in FINAL_LETTERS:
            for order_num in pair:
                similar_orders.add(order_num)

        letters = list(
            HebrewLetter.objects
            .filter(order__in=similar_orders)
            .order_by("order")
            .values("order", "letter", "name_en")
        )
        
        letters_by_order = {}
        for letter in letters:
            letters_by_order[letter["order"]] = {"letter": letter["letter"], "name_en": letter["name_en"], "order": letter["order"]}

        tuple_list = []
        for (a, b) in FINAL_LETTERS:
            if a in letters_by_order and b in letters_by_order:
                tuple_list.append([letters_by_order[a], letters_by_order[b]])

        questions = generate_final_letters_questions(tuple_list, session.seed)
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
    correct, match_debug = check_correctness(question, user_answer_json)

    LessonAnswer.objects.create(
        session=session,
        question_index=question_index,
        user_answer_json=user_answer_json,
        correct=correct,
        answered_at=timezone.now()
    )
    
    try:
        user = UserInformation.objects.get(firebase_uid=session.user_id)
        user.total_answers = (user.total_answers or 0) + 1
        if correct:
            user.total_correct_answers = (user.total_correct_answers or 0) + 1
        user.save(update_fields=["total_answers", "total_correct_answers"])
        check_answer_achievements(user)
    except UserInformation.DoesNotExist:
        pass
    
    session.current_index = max(session.current_index or 0, question_index + 1)
    
    if session.current_index >= len(questions):
        session.completed = True
        session.completed_at = timezone.now()

        correct_count = (
            LessonAnswer.objects
            .filter(session=session, correct=True)
            .values("question_index")
            .distinct()
            .count()
        )
        total_questions = len(questions)
        required_correct = ceil(total_questions * PASS_PERCENT) if total_questions else 0
        session.passed = total_questions > 0 and correct_count >= required_correct
    
    update_fields = ["current_index", "completed", "completed_at"]
    if session.completed:
        update_fields.append("passed")
    session.save(update_fields=update_fields)

    if session.completed and session.passed:
        try:
            user = UserInformation.objects.get(firebase_uid=session.user_id)
            check_lesson_achievements(user, session.lesson, session)
            
            today = timezone.now().date()
            today_count = LessonSession.objects.filter(
                user_id=session.user_id,
                completed=True,
                passed=True,
                completed_at__date=today,
            ).count()
            update_streaks_and_award(user, today_count)
        except UserInformation.DoesNotExist:
            pass
            

    result = {
        "correct": correct,
        "completed": session.completed,
        "current_index": session.current_index
    }
    if match_debug is not None:
        result["match_debug"] = match_debug
    return result
    
def _norm(s: str) -> str:
    return (s or "").strip().lower()


def _norm_final_letter_name(s: str) -> str:
    """Normalize final-letter name so 'final nun', 'nun final', and 'nun (final)' compare equal."""
    s = _norm(s or "")
    if not s:
        return s
    if s.startswith("final "):
        return s[6:].strip() + " (final)"
    if s.endswith(" final"):
        return s[:-6].strip() + " (final)"
    return s


def _norm_key(s) -> str:
    """Normalize string key (e.g. Hebrew letter) for consistent comparison."""
    if s is None:
        return ""
    s = (s or "").strip()
    try:
        import unicodedata
        return unicodedata.normalize("NFC", s)
    except Exception:
        return s


def _log_match_mismatch(question, user_answer, user_by_name, correct_by_name, reason):
    """Log why a match answer was marked wrong (for debugging)."""
    qp = question.get("pairs") or []
    up = user_answer.get("pairs") or []
    logger.warning(
        "Match marked incorrect: %s. correct_by_name=%s user_by_name=%s "
        "question_left_repr=%s user_left_repr=%s",
        reason,
        correct_by_name,
        user_by_name,
        [repr(p.get("left")) for p in qp],
        [repr(p.get("left")) for p in up],
    )


def check_correctness(question: dict, user_answer: dict) -> tuple[bool, dict | None]:
    """Returns (is_correct, match_debug_dict or None). match_debug_dict is set only for match type when wrong."""
    qtype = question.get("type")

    if qtype == "mc":
        return (user_answer.get("choice") == question.get("answer"), None)

    if qtype == "fill":
        correct_raw = question.get("answer") or ""
        user_raw = user_answer.get("answer") or ""
        if _norm(user_raw) == _norm(correct_raw):
            return (True, None)
        # Accept "final nun" / "nun final" as equivalent to "Nun (final)" for final-letter questions
        if "(final)" in _norm(correct_raw):
            if _norm_final_letter_name(user_raw) == _norm_final_letter_name(correct_raw):
                return (True, None)
        return (False, None)

    if qtype == "match":
        user_pairs = user_answer.get("pairs") or []
        correct_pairs = question.get("pairs") or []

        if len(user_pairs) != len(correct_pairs):
            return (False, None)

        def letters_by_name(pairs):
            out = {}
            for p in pairs:
                name = _norm(p.get("right"))
                letter = _norm_key(p.get("left"))
                out.setdefault(name, []).append(letter)
            for k in out:
                out[k] = sorted(out[k])
            return out

        user_by_name = letters_by_name(user_pairs)
        correct_by_name = letters_by_name(correct_pairs)

        def make_match_debug(reason):
            _log_match_mismatch(question, user_answer, user_by_name, correct_by_name, reason)
            return {
                "reason": reason,
                "correct_by_name": correct_by_name,
                "user_by_name": user_by_name,
                "question_left_repr": [repr(p.get("left")) for p in (question.get("pairs") or [])],
                "user_left_repr": [repr(p.get("left")) for p in user_pairs],
            }

        if set(user_by_name.keys()) != set(correct_by_name.keys()):
            return (False, make_match_debug("name set"))
        for name in correct_by_name:
            if user_by_name.get(name) != correct_by_name[name]:
                return (False, make_match_debug(name))
        return (True, None)

    raise ValueError(f"Unknown question type: {qtype}")

def review_items(user_id: str, lesson_slug:str):
    try:
        lesson = Lesson.objects.get(slug=lesson_slug)
    except:
        raise ValidationError("Unknown lesson")
    # Review should reflect what the user actually missed in any run of this lesson.
    # Do not require completed/passed here; include all sessions so the page always
    # matches what the quiz can pull from.
    lesson_sessions = (
        LessonSession.objects
        .filter(user_id=user_id, lesson=lesson)
        .order_by("started_at")
    )
    items = []
    for session in lesson_sessions:
        questions = session.question_set_json or []
        wrong_answers = LessonAnswer.objects.filter(session=session, correct=False)
        for answer in wrong_answers:
            if answer.question_index < 0 or answer.question_index >= len(questions):
                continue
            q = questions[answer.question_index]
            if q.get("type") == "mc" or q.get("type") == "fill":
                correct_answer = q.get("answer")
            elif q.get("type") == "match":
                correct_answer = q.get("pairs", [])
            else:
                correct_answer = q.get("answer")
                
            question_info = {
                "prompt": q.get("prompt"),
                "type": q.get("type"),
                "correct_answer": correct_answer,
                "user_answer": answer.user_answer_json
            }
            items.append(question_info)
    
    return items


def get_review_question_set(user_id: str, lesson_slug: str) -> list:
    """Return a list of full question dicts (for a review retake session) from wrong answers in the user's runs."""
    try:
        lesson = Lesson.objects.get(slug=lesson_slug)
    except Lesson.DoesNotExist:
        # Mirror start_lesson_session behavior
        raise ValidationError(f"Unknown lesson slug '{lesson_slug}'")

    sessions = (
        LessonSession.objects
        .filter(user_id=user_id, lesson=lesson)
        .order_by("started_at")
    )
    questions_list = []
    seen = set()
    session_ids = []
    total_wrong = 0
    for session in sessions:
        session_ids.append(session.id)
        questions = session.question_set_json or []
        wrong_answers = LessonAnswer.objects.filter(session=session, correct=False)
        total_wrong += wrong_answers.count()
        for answer in wrong_answers:
            if answer.question_index < 0 or answer.question_index >= len(questions):
                continue
            q = questions[answer.question_index]
            key = (
                q.get("prompt"),
                q.get("type"),
                str(q.get("answer") if q.get("type") != "match" else q.get("pairs"))
            )   
            if key in seen:
                continue
            seen.add(key)
            questions_list.append(dict(q))
    logger.warning(
        "Review question set built: lesson_slug=%s user_id=%s sessions=%s total_wrong_answers=%s unique_questions=%s",
        lesson_slug,
        user_id,
        session_ids,
        total_wrong,
        len(questions_list),
    )
    return questions_list

def start_review_lesson_session(user_id: str, lesson_slug: str) -> LessonSession:
    """Create a lesson session whose question set is the user's wrong questions from their runs."""
    question_set = get_review_question_set(user_id, lesson_slug)
    if not question_set:
        raise ValidationError("No questions to review for this lesson")
    lesson = Lesson.objects.get(slug=lesson_slug)
    session = LessonSession.objects.create(
        user_id=user_id,
        lesson=lesson,
        question_set_json=question_set,
        current_index=0,
        completed=False,
        seed=None,
    )
    return session


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
    
    # Prevent the pass count from contributing to progress after set quizes are completed
    pass_count = min(pass_count, required)
    
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
    
def get_lesson_2_combined_progress(user_id: str) -> dict:
    """ Get combined progress for Lesson 2 (similar-letters, begadkefat-letters, final-letters). 
    
    Lesson 2 is complete when all 3 sub-lessons have DEFAULT_PASSES_REQUIRED passes each. 
    Lesson 2 progress is the average of the 3 sub-lessons.
    
    Args:
        user_id: Firebase UID of the user
    
    Returns:
        Dictionary with progress_pct (0-100), is_complete (bool), similar_letters, begadkefat_letters, final_letters
    """
    from lessons.constants import LESSON_2_COMBINED_WEIGHT, DEFAULT_PASSES_REQUIRED
    
    p1 = get_user_lesson_progress(user_id, "similar-letters")
    p2 = get_user_lesson_progress(user_id, "begadkefat-letters")
    p3 = get_user_lesson_progress(user_id, "final-letters")
    similar_letters = p1 if p1 else {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    begadkefat_letters = p2 if p2 else {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    final_letters = p3 if p3 else {"pass_count": 0, "passes_required": DEFAULT_PASSES_REQUIRED, "progress_pct": 0, "is_complete": False}
    # Each contributes 33%
    combined_pct = (similar_letters["progress_pct"] *  LESSON_2_COMBINED_WEIGHT) + (begadkefat_letters["progress_pct"] * LESSON_2_COMBINED_WEIGHT) + (final_letters["progress_pct"] * LESSON_2_COMBINED_WEIGHT)
    is_complete = similar_letters["is_complete"] and begadkefat_letters["is_complete"] and final_letters["is_complete"]
    # For dashboard: total passes across all 3 quizzes, total required (3 × 4)
    total_pass_count = similar_letters["pass_count"] + begadkefat_letters["pass_count"] + final_letters["pass_count"]
    total_passes_required = similar_letters["passes_required"] + begadkefat_letters["passes_required"] + final_letters["passes_required"]
    # If complete, show 100%; otherwise use calculated percentage
    progress_pct = 100 if is_complete else min(100, int(combined_pct))
    return {
        "progress_pct": progress_pct,
        "is_complete": is_complete,
        "pass_count": total_pass_count,
        "passes_required": total_passes_required,
        "similar_letters": similar_letters,
        "begadkefat_letters": begadkefat_letters,
        "final_letters": final_letters,
    }