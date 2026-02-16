"""
Constants for lessons app.

This module contains all magic numbers and configuration values used throughout
the lessons application to ensure consistency and maintainability.
"""

# Question generation constants
MC_QUESTION_COUNT = 7
FILL_QUESTION_COUNT = 4
MATCH_QUESTION_COUNT = 4
TOTAL_QUESTIONS_PER_SESSION = MC_QUESTION_COUNT + FILL_QUESTION_COUNT + MATCH_QUESTION_COUNT

# Pass threshold
PASS_THRESHOLD = 12  # Minimum correct answers out of 15 to pass a lesson session

# Random seed range
RANDOM_SEED_MIN = 1
RANDOM_SEED_MAX = 500_000

# Letter range constants
ALPHABET_1_START = 1
ALPHABET_1_END = 11
ALPHABET_2_START = 12
ALPHABET_2_END = 22

# Letter range for special charaters 
BET = 2
GIMEL = 3
DALET = 4
HE = 5
VAV = 6
ZAYIN = 7
HET = 8
KAF = 11
MEM = 13
NUN = 14
PE = 17
TSADI = 18
RESH = 20
TAV = 22

# Pairs - (Bet, Kaf), (Dalet, Resh), (He, Het), (Vav, Zayin), (Gimel, Nun)
SIMILAR_LETTERS = {(BET, KAF), (DALET, RESH), (HE, HET), (VAV, ZAYIN), (GIMEL, NUN)}

BEGADKEFAT_LETTERS = {BET, GIMEL, DALET, KAF, PE, TAV}

FINAL_LETTERS = {KAF, MEM, PE, TSADI, NUN}

# Progress calculation constants
LESSON_1_COMBINED_WEIGHT = 0.5  # Each alphabet contributes 50% to lesson 1 progress
LESSON_2_COMBINED_WEIGHT = 0.33  # Each sub-lesson contributes 33% to lesson 2 progress
DEFAULT_PASSES_REQUIRED = 4  # Default number of passes required to complete a lesson

# Pagination
USERS_PER_PAGE = 25
