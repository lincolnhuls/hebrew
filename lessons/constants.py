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

# Progress calculation constants
LESSON_1_COMBINED_WEIGHT = 0.5  # Each alphabet contributes 50% to lesson 1 progress
DEFAULT_PASSES_REQUIRED = 4  # Default number of passes required to complete a lesson

# Pagination
USERS_PER_PAGE = 25
