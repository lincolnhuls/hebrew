from django.db import models

# Create your models here.
"""
LESSON RECIPE: alphabet-1

Goal:
- Recognize the first 11 Hebrew letters by name and symbol.

Content set:
- Letters 1–11 (Aleph–Kaf)

Question types to support (first version):
1) Multiple choice (name -> choose the correct letter)
2) Matching (pair letters with names)
3) Fill-in (given a letter, type/select its name)

Question mix (per session):
- MC: 7
- MATCH: 4
- FILL: 4
Total: 15 questions

Mastery rule:
- Pass if >= 12/15 correct

Answer acceptance:
- Fill-in: case-insensitive match on name (e.g., "Aleph", "aleph")
"""

"""
DATA WE WILL STORE PER SESSION (so refresh shows same questions):

- user_id (firebase_uid)
- lesson_slug
- question_set_json  # the generated questions for this run
- current_index
- completed (bool)
- started_at, completed_at
- answers stored as seperate rows (LessonAnswer)
"""

"""
CORE OBJECTS AND RELATIONSHIPS

Lesson
- Identifies a lesson (alphabet-1)
- Does NOT track progress
- Acts as a template / recipe

LessonSession
- One user's run through a lesson
- Belongs to exactly one Lesson
- Belongs to exactly one user
- Stores:
  - generated question set (JSON)
  - current question index
  - completion status
  - timestamps

LessonAnswer
- One answer to one question
- Belongs to exactly one LessonSession
- Stores:
  - question_index (position in question set)
  - user_answer (JSON)
  - correct (bool)
  - answered_at
"""

"""
MINIMUM DB FIELDS (recipe in code)

Lesson (static identifier only):
- slug
- title
- order

LessonSession (one run):
- user_id (firebase_uid)
- lesson (FK -> Lesson)
- question_set_json
- current_index
- completed
- started_at
- completed_at

LessonAnswer (one attempt):
- session (FK -> LessonSession)
- question_index  # NOT unique per session (multiple attempts allowed)
- user_answer_json
- correct
- answered_at
"""
class Lesson(models.Model):
    slug = models.SlugField(max_length=50, unique=True) 
    title = models.CharField(max_length=100)              
    order = models.PositiveSmallIntegerField()
    passes_required = models.PositiveSmallIntegerField(default=4)  # Duolingo-style: pass N times to complete
    
    class Meta:
        verbose_name = "Lesson"
        verbose_name_plural = "Lessons"
        ordering = ["order"]
    
    def __str__(self):
        return self.title

class LessonSession(models.Model):
    user_id = models.CharField(max_length=100, db_index=True)  # firebase_uid
    lesson = models.ForeignKey(Lesson, on_delete=models.CASCADE, related_name='sessions', db_index=True)
    question_set_json = models.JSONField(default=list)  # JSON string of generated questions
    current_index = models.PositiveSmallIntegerField(default=0)
    completed = models.BooleanField(default=False, db_index=True)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    seed = models.PositiveSmallIntegerField(null=True, blank=True)
    passed = models.BooleanField(default=False)  # True if this run met the pass threshold (e.g. >= 12/15)
    
    class Meta:
        verbose_name = "Lesson Session"
        verbose_name_plural = "Lesson Sessions"
        ordering = ["-started_at"]
        indexes = [
            models.Index(fields=['user_id', 'lesson', 'completed']),
            models.Index(fields=['user_id', 'completed', 'passed']),
        ]
    
    def __str__(self):
        return f"{self.lesson.title} - {self.user_id} ({'Completed' if self.completed else 'In Progress'})"
    
class LessonAnswer(models.Model):
    session = models.ForeignKey(LessonSession, on_delete=models.CASCADE, related_name='answers', db_index=True)
    question_index = models.PositiveSmallIntegerField()
    user_answer_json = models.JSONField()
    correct = models.BooleanField(db_index=True)
    answered_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Lesson Answer"
        verbose_name_plural = "Lesson Answers"
        ordering = ["session", "question_index", "-answered_at"]
        indexes = [
            models.Index(fields=['session', 'correct']),
            models.Index(fields=['session', 'question_index', 'correct']),
        ]
    
    def __str__(self):
        return f"Answer {self.question_index} - {'Correct' if self.correct else 'Incorrect'}"
    
    """
QUESTION SET JSON FORMAT (stored on LessonSession)

question_set_json = [
  {
    "type": "mc",
    "prompt": "Which letter is Aleph?",
    "choices": ["א", "ב", "ג", "ד"],
    "answer": "א"
  },
  {
    "type": "fill",
    "prompt": "What is the name of this letter?",
    "shown": "ב",
    "answer": "Bet"
  },
  {
    "type": "match",
    "prompt": "Match the letters to their names.",
    "pairs": [
      {"left": "א", "right": "Aleph"},
      {"left": "ב", "right": "Bet"},
      {"left": "ג", "right": "Gimel"}
    ]
  }
]
"""

"""
HEBREW LETTER DATA (teaching content)

Each letter must store:
- order (1–22)
- letter (א)
- name_en (Aleph)
- transliteration (optional, e.g. "ʾālef")
- notes (optional, future use)
"""

class HebrewLetter(models.Model):
    order = models.PositiveSmallIntegerField(unique=True)
    letter = models.CharField(max_length=5) 
    name_en = models.CharField(max_length=50)
    transliteration = models.CharField(max_length=100, blank=True, null=True)
    
    class Meta:
        verbose_name = "Hebrew Letter"
        verbose_name_plural = "Hebrew Letters"
        ordering = ["order"]
    
    def __str__(self):
        return f"{self.letter} ({self.name_en})"

"""
Alphabet 1 Question Generation (Deterministic)
Input - Letters 1-11
Counts - MC:7 MATCH:4 FILL:4
MC: Prompt = "Which letter is {name_en}?" Choices = correct letter + 3 random letters
FILL: Prompt = "What is the name of this letter?" Shown = letter, Answer = name_en
Match: Prompt = "Match the letters to their names." Pairs = 4 letters and thier 4 names(shuffled)
Determinism rule: "When a LessonSession is created, generate the full question set once using a stored seed, then save it to question_set_json."
"""