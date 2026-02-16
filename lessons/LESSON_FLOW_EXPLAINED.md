# Lesson Flow & Architecture – Reference for Lesson 2 Implementation

This document explains how Lesson 1 works end-to-end so you can implement Lesson 2 in the same pattern. Lesson 2 should have three quizzes (similar-letters, begadkefat, final-letters) instead of two.

---

## High-Level Flow

1. User visits **Lesson 1 Hub** (`/lesson-1/`) and sees three cards: Learn the Alphabet, Letters 1–11, Letters 12–22.
2. "Letters 1–11" and "Letters 12–22" link to the **Lesson Runner** with slugs `alphabet-1` and `alphabet-2`.
3. Lesson Runner loads questions via API, renders them (MC / fill / match), and submits answers.
4. Progress is tracked per lesson slug: each lesson needs `passes_required` (default 4) completed, passed sessions.
5. Lesson 1 is "complete" when **both** alphabet-1 and alphabet-2 are complete.

---

## File Map & Responsibilities

### URL Routing

| File | Responsibility |
|------|----------------|
| `hebrew/urls.py` | Top-level routing; includes `main.urls` at `""` and `lessons.urls` at `"lessons/"` |
| `main/urls.py` | Main app URLs: dashboard, lesson-1 hub, lesson-2 hub, lesson runner, alphabet learn, similar-letters, begadkefat, final-letters |
| `lessons/urls.py` | Lesson API URLs: `start/`, `resume/`, `<session_id>/current/`, `<session_id>/submit/` |

### Main App (main/)

| File | Responsibility |
|------|----------------|
| `main/views.py` | `dashboard`, `lesson_1_hub`, `lesson_2_hub`, `lesson_runner`, `alphabet_learn`, `similar_letters`, `begadkefat`, `final_letters` |
| `main/templates/main/dashboard.html` | Shows Lesson 1 & 2 cards; uses `lesson_1_combined` and `lesson_1_complete` from context |
| `main/templates/main/lesson_1_hub.html` | Lesson 1 hub: Learn Alphabet link + two quiz cards (Letters 1–11, Letters 12–22) with progress bars and Continue/Review buttons |
| `main/templates/main/lesson_2_hub.html` | Lesson 2 hub: Learn Special Letters link + placeholder quiz cards (Similar Letters Quiz, Special Letters Quiz) |
| `main/templates/main/lesson_runner.html` | Single-page quiz UI; receives `lesson_slug`, `lesson_title`, `user_id`; loads `lesson_runner.js` with config |
| `main/static/main/js/lesson_runner.js` | Calls `resume` or `start` API, renders MC/fill/match questions, submits answers, shows completion |
| `main/static/main/css/lesson_runner.css` | Styles for the lesson runner |

### Lessons App (lessons/)

| File | Responsibility |
|------|----------------|
| `lessons/models.py` | `Lesson` (slug, title, order, passes_required), `LessonSession` (user_id, lesson FK, question_set_json, current_index, completed, passed, seed), `LessonAnswer`, `HebrewLetter` |
| `lessons/services.py` | `start_lesson_session`, `submit_answer`, `get_user_lesson_progress`, `get_lesson_1_combined_progress`, `check_correctness` |
| `lessons/views.py` | API views: `start_lesson`, `resume_lesson`, `get_current_question`, `submit_answer_view` |
| `lessons/generators.py` | `generate_alphabet_1_questions`, `generate_alphabet_2_questions`; helpers `make_mc_question`, `make_fill_question`, `make_match_question` |
| `lessons/constants.py` | MC/FILL/MATCH counts, PASS_THRESHOLD (12/15), RANDOM_SEED_MIN/MAX, letter ranges, LESSON_1_COMBINED_WEIGHT, DEFAULT_PASSES_REQUIRED |

---

## Lesson Flow in Detail

### 1. Dashboard

- **View:** `main/views.py` → `dashboard`
- **Template:** `main/dashboard.html`
- **Context:** `lesson_1_combined` (from `get_lesson_1_combined_progress`), `lesson_1_complete`
- Dashboard shows Lesson 1 card with progress; Lesson 2 card is unlocked when Lesson 1 is complete.

### 2. Lesson 1 Hub

- **URL:** `/lesson-1/`
- **View:** `main/views.py` → `lesson_1_hub`
- **Template:** `main/lesson_1_hub.html`
- **Context:** `lesson_1_combined` (contains `alphabet_1`, `alphabet_2` with `pass_count`, `passes_required`, `progress_pct`, `is_complete`)
- Each quiz card links to `{% url 'main:lesson_runner' lesson_slug='alphabet-1' %}` or `alphabet-2`.

### 3. Lesson Runner (Quiz Page)

- **URL:** `/lesson/<slug:lesson_slug>/` (e.g. `/lesson/alphabet-1/`)
- **View:** `main/views.py` → `lesson_runner`
- **Template:** `main/lesson_runner.html`
- **Context:** `lesson_slug`, `lesson_title`, `user_id`, optionally `lesson_error`
- Template injects `LESSON_RUNNER_CONFIG` with `lessonSlug`, `lessonTitle`, `userId`, `resumeUrl`, `startUrl`, `submitUrlTemplate`.

### 4. Client-Side: lesson_runner.js

- On load, calls `lessons:resume_lesson` with `user_id` and `lesson_slug`.
- **Resume API** returns:
  - Incomplete session → current question
  - Completed session → results (score, passed)
  - No session → starts new session and returns first question
- Question formats:
  - **MC:** `{ type: "mc", prompt, choices: [...], answer }` (answer stripped before client)
  - **Fill:** `{ type: "fill", prompt, shown, answer }`
  - **Match:** `{ type: "match", prompt, pairs: [{ left, right }, ...] }`
- User submits; `lessons:submit_answer` returns `{ correct, completed, current_index, next_question?, ... }`.
- If `completed`, shows score and passed/failed; otherwise advances to next question.

### 5. Start Lesson Session (Backend)

- **API:** POST `/lessons/start/` (or invoked via resume when no session exists)
- **View:** `lessons/views.py` → `start_lesson` (or `resume_lesson` path 3)
- **Service:** `lessons/services.py` → `start_lesson_session(user_id, lesson_slug)`
- Logic:
  1. Fetch `Lesson` by slug.
  2. Create `LessonSession` with user_id, lesson, random seed.
  3. If `lesson_slug == "alphabet-2"`: fetch letters 12–22, call `generate_alphabet_2_questions`.
  4. Else (alphabet-1): fetch letters 1–11, call `generate_alphabet_1_questions`.
  5. Store questions in `session.question_set_json`.
- Returns first question (answer stripped) to client.

### 6. Submit Answer (Backend)

- **API:** POST `/lessons/<session_id>/submit/`
- **View:** `lessons/views.py` → `submit_answer_view`
- **Service:** `lessons/services.py` → `submit_answer(session_id, question_index, user_answer, user_id)`
- Logic:
  1. Validate session ownership, get question from `question_set_json[question_index]`.
  2. `check_correctness(question, user_answer)` → MC: `choice == answer`; Fill: normalized text match; Match: pairs comparison.
  3. Create `LessonAnswer` record.
  4. Advance `current_index`; if reached end, set `completed`, `completed_at`, and `passed` (correct_count >= PASS_THRESHOLD).
  5. Return result + next question if not completed.

### 7. Progress Calculation

- **Service:** `lessons/services.py` → `get_user_lesson_progress(user_id, lesson_slug)`
  - Counts `LessonSession` where `user_id`, `lesson__slug`, `completed=True`, `passed=True`.
  - Returns `{ pass_count, passes_required, progress_pct, is_complete }`.
- **Service:** `get_lesson_1_combined_progress(user_id)`
  - Gets progress for `alphabet-1` and `alphabet-2`.
  - Combined progress_pct = 50% each; `is_complete` = both complete.

---

## Database Models

- **Lesson:** slug (unique), title, order, passes_required (default 4)
- **LessonSession:** user_id, lesson FK, question_set_json, current_index, completed, passed, seed, started_at, completed_at
- **LessonAnswer:** session FK, question_index, user_answer_json, correct, answered_at

Lessons `alphabet-1` and `alphabet-2` exist via migrations (e.g. `lessons/migrations/0006_create_alphabet_1_lesson.py`).

---

## Question Generator Contract

Each generator has signature: `(letters_or_data, seed) -> list[dict]`.

- **alphabet-1 / alphabet-2:** `letters` = list of `{ letter, name_en }` from HebrewLetter.
- Output: list of questions with `type` in `"mc"`, `"fill"`, `"match"`.
- MC: `{ type, prompt, choices, answer }`
- Fill: `{ type, prompt, shown, answer }`
- Match: `{ type, prompt, pairs: [{ left, right }, ...] }`

`check_correctness` in `lessons/services.py` handles these types. User answers: MC `{ choice }`, Fill `{ answer }`, Match `{ pairs }`.

---

## What You Need for Lesson 2

1. **Create 3 Lesson records** (migration or admin): slugs `similar-letters`, `begadkefat`, `final-letters`.
2. **Add 3 generators** in `lessons/generators.py`: `generate_similar_letters_questions`, `generate_begadkefat_questions`, `generate_final_letters_questions`. Each returns the same question format (mc, fill, match).
3. **Extend `start_lesson_session`** in `lessons/services.py`: add `elif lesson_slug == "similar-letters"` etc., fetch appropriate content, call the right generator.
4. **Add `get_lesson_2_combined_progress`** in `lessons/services.py`: combine progress for all three lesson slugs (e.g. equal weight 1/3 each; complete when all three complete).
5. **Update `main/views.py`**: `lesson_2_hub` should pass `lesson_2_combined` from `get_lesson_2_combined_progress`.
6. **Update `main/templates/main/lesson_2_hub.html`**: Replace placeholder quiz cards with three cards (Similar Letters, Begadkefat, Final Letters) with progress bars and links to `lesson_runner` with the correct slugs.
7. **Update `main/templates/main/lesson_runner.html`**: Extend the Back link logic so it returns to `lesson_2_hub` when `lesson_slug` is one of the three Lesson 2 slugs.
8. **Optional:** Update dashboard to use `lesson_2_complete` when showing Lesson 3 locked state.

---

## Key File Paths (Project Root: hebrew/)

```
hebrew/
├── hebrew/urls.py
├── main/
│   ├── urls.py
│   ├── views.py
│   └── templates/main/
│       ├── dashboard.html
│       ├── lesson_1_hub.html
│       ├── lesson_2_hub.html
│       ├── lesson_runner.html
│       └── ...
├── main/static/main/
│   ├── js/lesson_runner.js
│   └── css/lesson_runner.css
└── lessons/
    ├── urls.py
    ├── views.py
    ├── models.py
    ├── services.py
    ├── generators.py
    ├── constants.py
    └── migrations/
```
