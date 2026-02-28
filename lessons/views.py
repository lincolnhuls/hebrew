import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.core.exceptions import ValidationError
from lessons.models import LessonSession, LessonAnswer, Lesson
from lessons.services import start_lesson_session, start_review_lesson_session, submit_answer
from lessons.constants import PASS_THRESHOLD

# Create your views here.
@require_POST
def start_review_quiz(request):
    """Start a review session (quiz made from wrong answers) and return session_id."""
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)
    user_id = payload.get("user_id")
    lesson_slug = payload.get("lesson_slug")
    if not user_id or not lesson_slug:
        return JsonResponse({"error": "user_id and lesson_slug required"}, status=400)
    try:
        session = start_review_lesson_session(user_id, lesson_slug)
    except Lesson.DoesNotExist:
        return JsonResponse({"error": f"Lesson '{lesson_slug}' not found"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    return JsonResponse({"session_id": session.id})


@require_POST
def start_lesson(request):
    """Start a new lesson session and return the first question."""
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    user_id = payload.get("user_id")
    lesson_slug = payload.get("lesson_slug")

    if not user_id or not lesson_slug:
        return JsonResponse({"error": "user_id and lesson_slug required"}, status=400)

    try:
        session = start_lesson_session(user_id, lesson_slug)
    except Lesson.DoesNotExist:
        return JsonResponse({"error": f"Lesson '{lesson_slug}' not found"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to start lesson: {str(e)}"}, status=500)

    # Validate question set exists and has questions
    if not session.question_set_json or len(session.question_set_json) == 0:
        return JsonResponse({"error": "Lesson has no questions"}, status=500)
    
    if session.current_index >= len(session.question_set_json):
        return JsonResponse({"error": "Invalid session state"}, status=500)
    
    try:
        first_q = session.question_set_json[session.current_index]
    except (IndexError, TypeError) as e:
        return JsonResponse({"error": "Invalid question index"}, status=500)

    return JsonResponse({
        "session_id": session.id,
        "current_index": session.current_index,
        "total_questions": len(session.question_set_json),
        "question_index": session.current_index,
        "question": _strip_answer(first_q),
    })
    
def resume_lesson(request):
    """Resume an existing lesson session or start a new one.
    
    Optional GET param session_id: if provided, load that session (must belong to user_id).
    
    Returns:
        - Incomplete session: Current question data
        - Completed session: Session results
        - No session: New session with first question
    """
    user_id = request.GET.get("user_id")
    lesson_slug = request.GET.get("lesson_slug")
    session_id_param = request.GET.get("session_id")

    if not user_id or not lesson_slug:
        return JsonResponse({"error": "user_id and lesson_slug required"}, status=400)

    # 0) If session_id given, load that session (for review retake)
    if session_id_param:
        try:
            sid = int(session_id_param)
            session = LessonSession.objects.select_related("lesson").filter(id=sid, user_id=user_id).first()
        except (ValueError, TypeError):
            session = None
        if session:
            if session.lesson.slug != lesson_slug:
                return JsonResponse({"error": "Session does not match lesson"}, status=400)
            idx = session.current_index
            questions = session.question_set_json or []
            if idx is None or idx < 0 or idx >= len(questions):
                if session.completed:
                    data = {"session_id": session.id, "completed": True}
                    data.update(_session_results(session.id))
                    return JsonResponse(data)
                return JsonResponse({"error": "Invalid session state"}, status=500)
            q = questions[idx]
            return JsonResponse({
                "session_id": session.id,
                "completed": False,
                "current_index": idx,
                "total_questions": len(session.question_set_json),
                "question_index": idx,
                "question": _strip_answer(q),
            })
        # session_id invalid or not found — fall through to normal resume

    # 1) Prefer an existing incomplete session
    session = (
        LessonSession.objects
        .select_related('lesson')
        .filter(user_id=user_id, lesson__slug=lesson_slug, completed=False)
        .order_by("-started_at")
        .first()
    )

    if session:
        idx = session.current_index
        questions = session.question_set_json or []

        # Detect a bad state
        if idx is None or idx < 0 or idx >= len(questions):
            session.delete()
            session = None
        else:
            try:
                q = questions[idx]
            except (IndexError, TypeError):
                session.delete()
                session = None
            else:
                # If valid session, return
                return JsonResponse({
                    "session_id": session.id,
                    "completed": False,
                    "current_index": idx,
                    "total_questions": len(session.question_set_json),
                    "question_index": idx,
                    "question": _strip_answer(q),
                })

    # 2) If none incomplete, return latest completed session results (if any)
    completed_session = (
        LessonSession.objects
        .select_related('lesson')
        .filter(user_id=user_id, lesson__slug=lesson_slug, completed=True)
        .order_by("-completed_at", "-started_at")
        .first()
    )

    if completed_session:
        data = {"session_id": completed_session.id, "completed": True}
        data.update(_session_results(completed_session.id))
        return JsonResponse(data)

    # 3) If no sessions exist at all, start a new one
    try:
        session = start_lesson_session(user_id, lesson_slug)
    except Lesson.DoesNotExist:
        return JsonResponse({"error": f"Lesson '{lesson_slug}' not found"}, status=404)
    except ValidationError as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to start lesson: {str(e)}"}, status=500)
    
    questions = session.question_set_json or []
    if session.current_index >= len(questions):
        return JsonResponse({"error": "Invalid session state"}, status=500)
    
    try:
        first_q = questions[session.current_index]
    except (IndexError, TypeError):
        return JsonResponse({"error": "Invalid question index"}, status=500)

    return JsonResponse({
        "session_id": session.id,
        "completed": False,
        "current_index": session.current_index,
        "total_questions": len(session.question_set_json),
        "question_index": session.current_index,
        "question": _strip_answer(first_q),
    })

def _strip_answer(question: dict) -> dict:
    """Remove answer data from question dict for client display.
    
    Args:
        question: Question dictionary with answer data
    
    Returns:
        Question dictionary with answer data removed
    """
    q = dict(question)
    
    if q["type"] in ("mc", "fill"):
        q.pop("answer", None)
        
    if q["type"] == "match":
        pass
    
    return q

def _session_results(session_id: int) -> dict:
    # distinct correct questions (so retries don’t inflate score)
    correct_count = (
        LessonAnswer.objects
        .filter(session_id=session_id, correct=True)
        .values("question_index")
        .distinct()
        .count()
    )
    total = (
        LessonSession.objects
        .filter(id=session_id)
        .values_list("question_set_json", flat=True)
        .first()
    )
    total_questions = len(total or [])
    passed = correct_count >= PASS_THRESHOLD

    return {
        "score_correct": correct_count,
        "total_questions": total_questions,
        "passed": passed,
    }


def get_current_question(request, session_id):
    """Get the current question for a lesson session.
    
    Args:
        request: Django request object (contains session with firebase_uid for ownership validation)
        session_id: ID of the lesson session
    
    Returns:
        JSON response with current question or completion status
    """
    user_id = request.session.get('firebase_uid')
    
    try:
        session = LessonSession.objects.select_related('lesson').get(id=session_id)
    except LessonSession.DoesNotExist:
        return JsonResponse({"error": "session not found"}, status=404)
    
    # Security: Validate session ownership
    if user_id and session.user_id != user_id:
        return JsonResponse({"error": "Access denied"}, status=403)
    
    if session.completed:
        return JsonResponse({
            "completed": True,
        })
    
    questions = session.question_set_json or []
    if not questions:
        return JsonResponse({"error": "Session has no questions"}, status=500)
        
    idx = session.current_index
    if idx >= len(questions):
        return JsonResponse({"error": "Invalid session state"}, status=500)
    
    try:
        question = questions[idx]
    except (IndexError, TypeError):
        return JsonResponse({"error": "Invalid question index"}, status=500)
    
    return JsonResponse({
        "completed": False,
        "question_index": idx,
        "question": _strip_answer(question)
    })
    
@require_POST
def submit_answer_view(request, session_id):
    """Submit an answer for a question in a lesson session.
    
    Args:
        request: Django request object with JSON payload containing question_index and user_answer
        session_id: ID of the lesson session
    
    Returns:
        JSON response with correctness, completion status, and next question if applicable
    """
    user_id = request.session.get('firebase_uid')
    
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    question_index = payload.get("question_index")
    user_answer = payload.get("user_answer")

    if question_index is None or user_answer is None:
        return JsonResponse({"error": "question_index and user_answer required"}, status=400)

    try:
        result = submit_answer(session_id, int(question_index), user_answer, user_id=user_id)
    except LessonSession.DoesNotExist:
        return JsonResponse({"error": "session not found"}, status=404)
    except (ValueError, IndexError) as e:
        return JsonResponse({"error": str(e)}, status=400)
    except Exception as e:
        return JsonResponse({"error": f"Failed to submit answer: {str(e)}"}, status=500)

    # If completed, nothing else to return
    if result.get("completed"):
        result.update(_session_results(session_id))
        return JsonResponse(result)

    # Otherwise attach next question (answer stripped)
    # Reuse session data from submit_answer result if available, otherwise fetch
    try:
        session = LessonSession.objects.select_related('lesson').get(id=session_id)
    except LessonSession.DoesNotExist:
        return JsonResponse({"error": "session not found"}, status=404)
    
    idx = result.get("current_index", session.current_index)
    questions = session.question_set_json or []
    
    if idx >= len(questions):
        return JsonResponse({"error": "Invalid session state"}, status=500)
    
    try:
        next_q = questions[idx]
    except (IndexError, TypeError):
        return JsonResponse({"error": "Invalid question index"}, status=500)

    result["next_question_index"] = idx
    result["next_question"] = _strip_answer(next_q)

    return JsonResponse(result)
