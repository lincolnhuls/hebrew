from django.test import TestCase
from random import Random

from lessons.services import check_correctness
from lessons.generators import make_begadkefat_letters_match_question


# Hebrew letters (Unicode) for consistent tests
BET_DAGESH = "\u05d1\u05bc"   # בּ
BET = "\u05d1"                 # ב
PE_DAGESH = "\u05e4\u05bc"     # פּ
PE = "\u05e4"                  # פ
GIMEL = "\u05d2"               # ג


class CheckCorrectnessMatchTests(TestCase):
    """Tests for match-question validation (e.g. begadkefat letter→name)."""

    def test_match_correct_bet_vet(self):
        """Correct assignment: בּ→Bet, ב→Vet is accepted."""
        question = {
            "type": "match",
            "pairs": [
                {"left": BET_DAGESH, "right": "Bet"},
                {"left": BET, "right": "Vet"},
            ],
        }
        user_answer = {
            "pairs": [
                {"left": BET_DAGESH, "right": "Bet"},
                {"left": BET, "right": "Vet"},
            ],
        }
        self.assertTrue(check_correctness(question, user_answer)[0])

    def test_match_swapped_bet_vet_fails(self):
        """Swapped: ב→Bet, בּ→Vet is rejected."""
        question = {
            "type": "match",
            "pairs": [
                {"left": BET_DAGESH, "right": "Bet"},
                {"left": BET, "right": "Vet"},
            ],
        }
        user_answer = {
            "pairs": [
                {"left": BET, "right": "Bet"},
                {"left": BET_DAGESH, "right": "Vet"},
            ],
        }
        self.assertFalse(check_correctness(question, user_answer)[0])

    def test_match_correct_pe_fe(self):
        """Correct assignment: פּ→Pe, פ→Fe is accepted."""
        question = {
            "type": "match",
            "pairs": [
                {"left": PE_DAGESH, "right": "Pe"},
                {"left": PE, "right": "Fe"},
            ],
        }
        user_answer = {
            "pairs": [
                {"left": PE_DAGESH, "right": "Pe"},
                {"left": PE, "right": "Fe"},
            ],
        }
        self.assertTrue(check_correctness(question, user_answer)[0])

    def test_match_swapped_pe_fe_fails(self):
        """Swapped: פ→Pe, פּ→Fe is rejected."""
        question = {
            "type": "match",
            "pairs": [
                {"left": PE_DAGESH, "right": "Pe"},
                {"left": PE, "right": "Fe"},
            ],
        }
        user_answer = {
            "pairs": [
                {"left": PE, "right": "Pe"},
                {"left": PE_DAGESH, "right": "Fe"},
            ],
        }
        self.assertFalse(check_correctness(question, user_answer)[0])

    def test_match_shared_name_both_correct(self):
        """When two letters share one name (e.g. Gimel), both assigned that name is correct."""
        question = {
            "type": "match",
            "pairs": [
                {"left": GIMEL, "right": "Gimel"},
                {"left": GIMEL, "right": "Gimel"},
            ],
        }
        # User picks "Gimel" for both rows (order of rows doesn't matter)
        user_answer = {
            "pairs": [
                {"left": GIMEL, "right": "Gimel"},
                {"left": GIMEL, "right": "Gimel"},
            ],
        }
        self.assertTrue(check_correctness(question, user_answer)[0])

    def test_match_wrong_name_for_letter_fails(self):
        """Wrong name for a letter is rejected."""
        question = {
            "type": "match",
            "pairs": [
                {"left": BET_DAGESH, "right": "Bet"},
                {"left": BET, "right": "Vet"},
            ],
        }
        user_answer = {
            "pairs": [
                {"left": BET_DAGESH, "right": "Vet"},
                {"left": BET, "right": "Gimel"},
            ],
        }
        self.assertFalse(check_correctness(question, user_answer)[0])

    def test_match_pair_count_mismatch_fails(self):
        """Different number of pairs is rejected."""
        question = {
            "type": "match",
            "pairs": [
                {"left": BET_DAGESH, "right": "Bet"},
                {"left": BET, "right": "Vet"},
            ],
        }
        user_answer = {
            "pairs": [{"left": BET_DAGESH, "right": "Bet"}],
        }
        self.assertFalse(check_correctness(question, user_answer)[0])

    def test_match_normalization_case_insensitive(self):
        """Name comparison is case-insensitive (normalized)."""
        question = {
            "type": "match",
            "pairs": [{"left": GIMEL, "right": "Gimel"}],
        }
        user_answer = {
            "pairs": [{"left": GIMEL, "right": "gimel"}],
        }
        self.assertTrue(check_correctness(question, user_answer)[0])

    def test_begadkefat_generator_assigns_bet_vet_correctly(self):
        """Generator uses name_en for dagesh form (Bet) and dagesh_name for base (Vet)."""
        # DB-style: base (order 2) has name_en="Bet", dagesh_name="Vet"; dagesh (order 23) same.
        tuple_list = [
            [
                {"letter": BET, "order": 2, "name_en": "Bet", "dagesh_name": "Vet"},
                {"letter": BET_DAGESH, "order": 23, "name_en": "Bet", "dagesh_name": "Vet"},
            ],
            [
                {"letter": PE, "order": 17, "name_en": "Pe", "dagesh_name": "Fe"},
                {"letter": PE_DAGESH, "order": 27, "name_en": "Pe", "dagesh_name": "Fe"},
            ],
        ]
        rng = Random(42)
        q = make_begadkefat_letters_match_question(tuple_list, rng)
        pairs = {p["left"]: p["right"] for p in q["pairs"]}
        self.assertEqual(pairs[BET], "Vet", "Base ב should be Vet")
        self.assertEqual(pairs[BET_DAGESH], "Bet", "Dagesh בּ should be Bet")
        self.assertEqual(pairs[PE], "Fe", "Base פ should be Fe")
        self.assertEqual(pairs[PE_DAGESH], "Pe", "Dagesh פּ should be Pe")

    def test_match_unicode_normalization_letter_key(self):
        """Letter keys are normalized (NFC) so NFD from frontend matches question."""
        import unicodedata
        # בּ in NFC vs NFD (same logical character)
        bet_dagesh_nfc = "\u05d1\u05bc"
        bet_dagesh_nfd = unicodedata.normalize("NFD", bet_dagesh_nfc)
        question = {
            "type": "match",
            "pairs": [{"left": bet_dagesh_nfc, "right": "Bet"}],
        }
        user_answer = {
            "pairs": [{"left": bet_dagesh_nfd, "right": "Bet"}],
        }
        self.assertTrue(check_correctness(question, user_answer)[0])
