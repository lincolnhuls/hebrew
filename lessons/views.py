import json
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from lessons.models import LessonSession, LessonAnswer
from lessons.services import start_lesson_session, submit_answer

# Create your views here.
@require_POST
def start_lesson(request):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    user_id = payload.get("user_id")
    lesson_slug = payload.get("lesson_slug")

    if not user_id or not lesson_slug:
        return JsonResponse({"error": "user_id and lesson_slug required"}, status=400)

    session = start_lesson_session(user_id, lesson_slug)

    first_q = session.question_set_json[session.current_index]

    return JsonResponse({
        "session_id": session.id,
        "current_index": session.current_index,
        "total_questions": len(session.question_set_json),
        "question_index": session.current_index,
        "question": _strip_answer(first_q),
    })
    
def resume_lesson(request):
    user_id = request.GET.get("user_id")
    lesson_slug = request.GET.get("lesson_slug")

    if not user_id or not lesson_slug:
        return JsonResponse({"error": "user_id and lesson_slug required"}, status=400)

    # 1) Prefer an existing incomplete session
    session = (
        LessonSession.objects
        .filter(user_id=user_id, lesson__slug=lesson_slug, completed=False)
        .order_by("-started_at")
        .first()
    )

    if session:
        idx = session.current_index
        q = session.question_set_json[idx]
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
        .filter(user_id=user_id, lesson__slug=lesson_slug, completed=True)
        .order_by("-completed_at", "-started_at")
        .first()
    )

    if completed_session:
        data = {"session_id": completed_session.id, "completed": True}
        data.update(_session_results(completed_session.id))
        return JsonResponse(data)

    # 3) If no sessions exist at all, start a new one
    session = start_lesson_session(user_id, lesson_slug)
    first_q = session.question_set_json[session.current_index]

    return JsonResponse({
        "session_id": session.id,
        "completed": False,
        "current_index": session.current_index,
        "total_questions": len(session.question_set_json),
        "question_index": session.current_index,
        "question": _strip_answer(first_q),
    })

def _strip_answer(question: dict) -> dict:
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
    passed = correct_count >= 12

    return {
        "score_correct": correct_count,
        "total_questions": total_questions,
        "passed": passed,
    }


def get_current_question(request, session_id):
    try:
        session = LessonSession.objects.get(id=session_id)
    except LessonSession.DoesNotExist:
        return JsonResponse({"error": "session not found"}, status=404)
    
    if session.completed:
        return JsonResponse({
            "completed": True,
        })
        
    idx = session.current_index
    question = session.question_set_json[idx]
    
    return JsonResponse({
        "completed": False,
        "question_index": idx,
        "question": _strip_answer(question)
    })
    
@require_POST
def submit_answer_view(request, session_id):
    try:
        payload = json.loads(request.body.decode("utf-8") or "{}")
    except json.JSONDecodeError:
        return JsonResponse({"error": "Invalid JSON body"}, status=400)

    question_index = payload.get("question_index")
    user_answer = payload.get("user_answer")

    if question_index is None or user_answer is None:
        return JsonResponse({"error": "question_index and user_answer required"}, status=400)

    try:
        result = submit_answer(session_id, int(question_index), user_answer)
    except (ValueError, IndexError) as e:
        return JsonResponse({"error": str(e)}, status=400)

    # If completed, nothing else to return
    if result.get("completed"):
        result.update(_session_results(session_id))
        return JsonResponse(result)


    # Otherwise attach next question (answer stripped)
    session = LessonSession.objects.get(id=session_id)
    idx = session.current_index
    next_q = session.question_set_json[idx]

    result["next_question_index"] = idx
    result["next_question"] = _strip_answer(next_q)

    return JsonResponse(result)
