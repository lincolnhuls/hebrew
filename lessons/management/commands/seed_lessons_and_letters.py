from django.core.management.base import BaseCommand
from lessons.models import Lesson, HebrewLetter
from lessons.constants import (
    ALPHABET_1_START,
    ALPHABET_1_END,
    ALPHABET_2_START,
    ALPHABET_2_END,
    DEFAULT_PASSES_REQUIRED,
)


class Command(BaseCommand):
    help = "Seed core lesson definitions and Hebrew letters into the database."

    def handle(self, *args, **options):
        self.stdout.write("Seeding lessons and Hebrew letters...")

        self._seed_lessons()
        self._seed_letters()

        self.stdout.write(self.style.SUCCESS("Seeding complete."))

    def _seed_lessons(self):
        lesson_defs = [
            ("alphabet-1", "Lesson 1: Aleph-Bet", 1),
            ("alphabet-2", "Lesson 2: Aleph-Bet II", 2),
            ("similar-letters", "Lesson 3: Similar Letters", 3),
            ("begadkefat-letters", "Lesson 4: Begadkefat Letters", 4),
            ("final-letters", "Lesson 5: Final Form Letters", 5),
        ]

        for slug, title, order in lesson_defs:
            obj, created = Lesson.objects.update_or_create(
                slug=slug,
                defaults={
                    "title": title,
                    "order": order,
                    "passes_required": DEFAULT_PASSES_REQUIRED,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} lesson: {slug} -> {title}")

    def _seed_letters(self):
        # Base 22 letters (orders 1–22)
        base_letters = [
            (1, "א", "Aleph"),
            (2, "ב", "Bet"),
            (3, "ג", "Gimel"),
            (4, "ד", "Dalet"),
            (5, "ה", "He"),
            (6, "ו", "Vav"),
            (7, "ז", "Zayin"),
            (8, "ח", "Het"),
            (9, "ט", "Tet"),
            (10, "י", "Yod"),
            (11, "כ", "Kaf"),
            (12, "ל", "Lamed"),
            (13, "מ", "Mem"),
            (14, "נ", "Nun"),
            (15, "ס", "Samekh"),
            (16, "ע", "Ayin"),
            (17, "פ", "Pe"),
            (18, "צ", "Tsade"),
            (19, "ק", "Qof"),
            (20, "ר", "Resh"),
            (21, "ש", "Shin"),
            (22, "ת", "Tav"),
        ]

        # Begadkefat dagesh forms (orders 23–28)
        dagesh_letters = [
            (23, "בּ", "Bet (b)", "Vet (v)"),
            (24, "גּ", "Gimel (g)", "Gimel (soft)"),
            (25, "דּ", "Dalet (d)", "Dalet (soft)"),
            (26, "כּ", "Kaf (k)", "Kaf (kh)"),
            (27, "פּ", "Pe (p)", "Fe (f)"),
            (28, "תּ", "Tav (t)", "Tav (soft)"),
        ]

        # Final forms (orders 29–33)
        final_letters = [
            (29, "ך", "Kaf (final)"),
            (30, "ם", "Mem (final)"),
            (31, "ן", "Nun (final)"),
            (32, "ף", "Pe (final)"),
            (33, "ץ", "Tsade (final)"),
        ]

        # Seed base letters
        for order, letter, name_en in base_letters:
            obj, created = HebrewLetter.objects.update_or_create(
                order=order,
                defaults={
                    "letter": letter,
                    "name_en": name_en,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} base letter {order}: {letter} ({name_en})")

        # Seed begadkefat letters
        for order, letter, name_en, dagesh_name in dagesh_letters:
            obj, created = HebrewLetter.objects.update_or_create(
                order=order,
                defaults={
                    "letter": letter,
                    "name_en": name_en,
                    "dagesh_name": dagesh_name,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} dagesh letter {order}: {letter} ({name_en} / {dagesh_name})")

        # Seed final-form letters
        for order, letter, name_en in final_letters:
            obj, created = HebrewLetter.objects.update_or_create(
                order=order,
                defaults={
                    "letter": letter,
                    "name_en": name_en,
                },
            )
            action = "Created" if created else "Updated"
            self.stdout.write(f"{action} final letter {order}: {letter} ({name_en})")

