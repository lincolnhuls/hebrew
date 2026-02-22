# Lessons App Management Commands

Reference for management commands in the `lessons` app. Run from the project root:

```bash
python manage.py <command> [args] [options]
```

---

## reset_lesson_progress

Reset lesson progress for a user by deleting all `LessonSession` records.

**Usage:**
```bash
python manage.py reset_lesson_progress <firebase_uid> [--dry-run]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `user_id` | Yes | Firebase UID of the user whose progress to reset |

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be deleted without actually deleting |

**Examples:**
```bash
python manage.py reset_lesson_progress abc123xyz
python manage.py reset_lesson_progress abc123xyz --dry-run
```

---

## reset_lesson

Reset progress for a specific lesson by deleting all `LessonSession` records for a user and lesson combination.

**Usage:**
```bash
python manage.py reset_lesson <firebase_uid> <lesson_slug> [--dry-run]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `user_id` | Yes | Firebase UID of the user whose progress to reset |
| `lesson_slug` | Yes | Lesson slug to reset (e.g. `alphabet-1`, `begadkefat-letters`, `similar-letters`) |

**Options:**
| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would be deleted without actually deleting |

**Examples:**
```bash
# Reset begadkefat-letters progress for a user
python manage.py reset_lesson abc123xyz begadkefat-letters

# Preview what would be deleted
python manage.py reset_lesson abc123xyz begadkefat-letters --dry-run

# Reset alphabet-1 progress
python manage.py reset_lesson abc123xyz alphabet-1
```

---

## fill_lesson_progress

Fill lesson progress for a user by creating completed, passed `LessonSession` records to meet `passes_required` per lesson.

**Usage:**
```bash
python manage.py fill_lesson_progress <firebase_uid> [--lesson SLUG] [--dry-run]
```

**Arguments:**
| Argument | Required | Description |
|----------|----------|-------------|
| `user_id` | Yes | Firebase UID of the user whose progress to fill |

**Options:**
| Option | Description |
|--------|-------------|
| `--lesson SLUG` | Fill only the specified lesson (e.g. `alphabet-1`, `alphabet-2`). Omit to fill all lessons |
| `--dry-run` | Show what would be created without actually creating |

**Examples:**
```bash
# Fill all lessons for a user
python manage.py fill_lesson_progress abc123xyz

# Fill only alphabet-1
python manage.py fill_lesson_progress abc123xyz --lesson alphabet-1

# Preview without changes
python manage.py fill_lesson_progress abc123xyz --dry-run
```

---
