from random import Random
from lessons.constants import MC_QUESTION_COUNT, FILL_QUESTION_COUNT, MATCH_QUESTION_COUNT

def make_mc_question(letters, rng):
    """Create a multiple choice question asking which letter matches a given name.
    
    Args:
        letters: List of letter dictionaries with 'letter' and 'name_en' keys
        rng: Random number generator instance
    
    Returns:
        Dictionary with 'type', 'prompt', 'choices', and 'answer' keys
    """
    target = rng.choice(letters)
    correct = target["letter"]
    
    distract_pool = [x for x in letters if x["letter"] != correct]
    distractors = rng.sample(distract_pool, 3)
    
    choices = [correct] + [d["letter"] for d in distractors]
    rng.shuffle(choices)
    
    return {
        "type": "mc",
        "prompt": f"Which letter is {target['name_en']}?",
        "choices": choices,
        "answer": correct
    }
    
def make_similar_letters_mc_question(tuple_list, rng):
    """Create a multiple choice question asking which letter matches a given name, but only comparing similar letters."""
    letter_tuple = rng.choice(tuple_list)
    letter1, letter2 = letter_tuple
    target = rng.choice([letter1, letter2])
    correct = target["letter"]
    
    distractor = letter2 if target == letter1 else letter1
    
    choices = [correct, distractor["letter"]]
    rng.shuffle(choices)
    
    return {
        "type": "mc",
        "prompt": f"Which letter is {target['name_en']}?",
        "choices": choices,
        "answer": correct
    }

def make_begadkefat_letters_mc_question(tuple_list, rng):
    """Create a multiple choice question asking which letter matches a given name, but only comparing begadkefat pairs"""
    letter_tuple = rng.choice(tuple_list)
    letter1, letter2 = letter_tuple
    target = rng.choice([letter1, letter2])
    correct = target["letter"]

    distractor = letter2 if target == letter1 else letter1

    choices = [correct, distractor["letter"]]
    rng.shuffle(choices)

    if target["order"] in (2, 17):
        name = target["dagesh_name"]
        name += ""
    else:
        name = target["name_en"]

    return {
        "type": "mc",
        "prompt": f"Which letter is {name}?",
        "choices": choices,
        "answer": correct
    }
    
def make_final_letters_mc_question(tuple_list, rng):
    """Create a multiple choice question using the final letter pairs"""
    letter_tuple = rng.choice(tuple_list)
    letter1, letter2 = letter_tuple
    target = rng.choice([letter1, letter2])
    correct = target["letter"]
    
    distractor = letter2 if target == letter1 else letter1
    
    choices = [correct, distractor["letter"]]
    rng.shuffle(choices)
    
    name = target["name_en"]
    
    return {
        "type": "mc",
        "prompt": f"Which letter is {name}?",
        "choices": choices,
        "answer": correct
    }
    
def make_fill_question(letters, rng):
    """Create a fill-in question asking for the name of a given letter.
    
    Args:
        letters: List of letter dictionaries with 'letter' and 'name_en' keys
        rng: Random number generator instance
    
    Returns:
        Dictionary with 'type', 'prompt', 'shown', and 'answer' keys
    """
    target = rng.choice(letters)
    return {
        "type": "fill",
        "prompt": "What is the name of this letter?",
        "shown": target["letter"],
        "answer": target["name_en"]
    }
    
def make_similar_letters_fill_question(tuple_list, rng):
    """Create a fill-in question asking for the name of a given letter, but only comparing similar letters."""
    letters = []
    for letter_tuple in tuple_list:
        letters.extend(letter_tuple)
    
    target = rng.choice(letters)
    return {
        "type": "fill",
        "prompt": "What is the name of this letter?",
        "shown": target["letter"],
        "answer": target["name_en"]
    }

def make_begadkefat_letters_fill_question(tuple_list, rng):
    """Create a fill in question asking for the name of a given letter, but only begadkefat pairs"""
    letters = []
    for letter_tuple in tuple_list:
        letters.extend(letter_tuple)

    target = rng.choice(letters)

    if target["order"] in (2, 17):
        name = target["dagesh_name"]
    else:
        name = target["name_en"]

    return {
        "type": "fill",
        "prompt": "What is the name of this letter?",
        "shown": target["letter"],
        "answer": name
    }
    
def make_final_letters_fill_question(tuple_list, rng):
    """Create a fill in the blank question using final letter pairs"""
    letters = []
    for letter_tuple in tuple_list:
        letters.extend(letter_tuple)
        
    target = rng.choice(letters)
    
    name = target["name_en"]
    
    return {
        "type": "fill",
        "prompt": "What is the name of this letter?",
        "shown": target["letter"],
        "answer": name
    }
    
def make_match_question(letters, rng):
    """Create a matching question pairing letters with their names.
    
    Args:
        letters: List of letter dictionaries with 'letter' and 'name_en' keys
        rng: Random number generator instance
    
    Returns:
        Dictionary with 'type', 'prompt', and 'pairs' keys
    """
    selected = rng.sample(letters, 4)
    
    pairs = [{"left": x["letter"], "right": x["name_en"]} for x in selected]
    rng.shuffle(pairs)
    
    return {
        "type": "match",
        "prompt": "Match the letters to their names.",
        "pairs": pairs
    }
    
def make_similar_letters_match_question(tuple_list, rng):
    """Create a matching question pairing letters with their names, but only comparing similar letters.
    Uses two distinct pairs so the four choices have no doubles."""
    if len(tuple_list) < 2:
        pair1 = pair2 = tuple_list[0]
    else:
        pair1, pair2 = rng.sample(tuple_list, 2)
    selected = [pair1[0], pair1[1], pair2[0], pair2[1]]
    pairs = [{"left": x["letter"], "right": x["name_en"]} for x in selected]
    rng.shuffle(pairs)
    
    return {
        "type": "match",
        "prompt": "Match the letters to their names.",
        "pairs": pairs
    }
    
def make_final_letters_match_questions(tuple_list, rng):
    if len(tuple_list) < 2:
        pair1 = pair2 = tuple_list[0]
    else:
        pair1, pair2 = rng.sample(tuple_list, 2)
    selected = [pair1[0], pair1[1], pair2[0], pair2[1]]
    pairs = [{"left": x["letter"], "right": x["name_en"]} for x in selected]
    rng.shuffle(pairs)
    
    return {
        "type": "match",
        "prompt": "Match the letters to their names.",
        "pairs": pairs
    }

def make_begadkefat_letters_match_question(tuple_list, rng):
    """Create a matching question pairing letters with their names, but only begadkefat pairs. 
    Uses two distrinct pairs so the four choices have no doubles
    """
    if not tuple_list:
        raise ValueError("No begadkefat pairs available to generate a question")

    if len(tuple_list) < 2:
        pair1 = pair2 = tuple_list[0]
    else:
        pair1, pair2 = rng.sample(tuple_list, 2)
    selected = [pair1[0], pair1[1], pair2[0], pair2[1]]
    # Plosive name (Bet, Pe, etc.) for dagesh form; fricative (Vet, Fe) for base.
    # DB stores: dagesh form has plosive in name_en, base has fricative in dagesh_name (or vice versa).
    # Use name_en for dagesh orders (plosive) and dagesh_name for base (fricative).
    DAGESH_ORDERS = (23, 24, 25, 26, 27, 28)
    pairs = []
    for x in selected:
        right = (
            x["name_en"] if x["order"] in DAGESH_ORDERS else (x.get("dagesh_name") or x["name_en"])
        ) or x.get("name_en") or x.get("dagesh_name") or ""
        pairs.append({
            "left": x["letter"],
            "right": right,
            "order": x["order"],
            "dagesh_name": x.get("dagesh_name"),
            "name_en": x.get("name_en")
        })
    rng.shuffle(pairs)

    return {
        "type": "match",
        "prompt": "Match the letters to their names.",
        "pairs": pairs
    }
    
def _generate_similar_letters_questions(letters, seed, mc_count=MC_QUESTION_COUNT, fill_count=FILL_QUESTION_COUNT, match_count=MATCH_QUESTION_COUNT):
    """
    Generate questions for similar letters, but only compare similar letters
    """
    rng = Random(seed)
    questions = []
    
    for _ in range(mc_count):
        questions.append(make_similar_letters_mc_question(letters, rng))
        
    for _ in range(fill_count):
        questions.append(make_similar_letters_fill_question(letters, rng))
        
    for _ in range(match_count):
        questions.append(make_similar_letters_match_question(letters, rng))
        
    rng.shuffle(questions)
    return questions
    
def _generate_begadkefat_letters_questions(letters, seed, mc_count=MC_QUESTION_COUNT, fill_count=FILL_QUESTION_COUNT, match_count=MATCH_QUESTION_COUNT):
    """
    Generate question for begadkefat letters, but only compare dagesh versions
    """
    rng = Random(seed)
    questions = []

    for _ in range(15):
        questions.append(make_begadkefat_letters_match_question(letters, rng))

    rng.shuffle(questions)
    return questions

def _generate_final_letters_questions(letters, seed, mc_count=MC_QUESTION_COUNT, fill_count=FILL_QUESTION_COUNT, match_count=MATCH_QUESTION_COUNT):
    """
    Generate questions for the final letters quiz based on final letter pairs"""
    rng = Random(seed)
    questions = []
    
    for _ in range(mc_count):
        questions.append(make_final_letters_mc_question(letters, rng))
        
    for _ in range(fill_count):
        questions.append(make_final_letters_fill_question(letters, rng))
        
    for _ in range(match_count):
        questions.append(make_final_letters_match_questions(letters, rng))
        
    rng.shuffle(questions)
    return questions
    

def _generate_alphabet_questions(letters, seed, mc_count=MC_QUESTION_COUNT, fill_count=FILL_QUESTION_COUNT, match_count=MATCH_QUESTION_COUNT):
    """Generate alphabet questions with specified counts for each question type.
    
    Args:
        letters: List of letter dictionaries with 'letter' and 'name_en' keys
        seed: Random seed for deterministic question generation
        mc_count: Number of multiple choice questions (default: 7)
        fill_count: Number of fill-in questions (default: 4)
        match_count: Number of matching questions (default: 4)
    
    Returns:
        List of shuffled question dictionaries
    """
    rng = Random(seed)
    questions = []
    
    for _ in range(mc_count):
        questions.append(make_mc_question(letters, rng))
    
    for _ in range(fill_count):
        questions.append(make_fill_question(letters, rng))
    
    for _ in range(match_count):
        questions.append(make_match_question(letters, rng))
    
    rng.shuffle(questions)
    return questions

from random import Random


def generate_vowels_1_questions(vowels: list[dict], seed: int) -> list[dict]:
    """
    Build a small question set for vowels.

    vowels: list of dicts with keys: symbol, name_en, transliteration (optional)
    """
    rng = Random(seed)
    questions: list[dict] = []

    # Base consonant so the niqqud is clearly visible
    base = "בּ"

    def display(symbol: str) -> str:
        """Return what the learner sees for a given vowel symbol."""
        return base + (symbol or "")

    def _has_visible_symbol(symbol: str) -> bool:
        """
        Heuristic: treat symbols that render as effectively empty as unusable.
        This guards against bad/placeholder data that would produce blank boxes.
        """
        if not symbol:
            return False
        # Strip common whitespace; keep combining marks themselves.
        if symbol.strip() == "":
            return False
        return True

    # Filter out any vowels without a usable symbol (defensive)
    usable_vowels = [v for v in vowels if _has_visible_symbol(v.get("symbol"))]
    if len(usable_vowels) < 2:
        return []

    # Build a canonical list of distinct symbols so distractors are visually unique
    symbol_to_vowel = {}
    for v in usable_vowels:
        sym = v["symbol"]
        if sym not in symbol_to_vowel:
            symbol_to_vowel[sym] = v
    distinct_symbols = list(symbol_to_vowel.keys())

    # 1) Multiple-choice: name -> symbol
    # "Which vowel is Patach?"
    for v in usable_vowels:
        correct_symbol = v["symbol"]
        name = v["name_en"]

        # Distinct other symbols for distractors
        other_symbols = [s for s in distinct_symbols if s != correct_symbol]
        if not other_symbols:
            continue

        # Aim for 4 total choices when possible
        k = 3 if len(other_symbols) >= 3 else len(other_symbols)
        distractor_symbols = rng.sample(other_symbols, k=k)
        symbols = [correct_symbol] + distractor_symbols
        rng.shuffle(symbols)

        # Build choices and defensively drop anything that renders "empty"
        choices = [display(s) for s in symbols]
        choices = [c for c in choices if c and c.strip()]
        # Require at least 2 visible options; otherwise skip this question
        if len(choices) < 2 or display(correct_symbol) not in choices:
            continue

        answer = display(correct_symbol)

        questions.append({
            "type": "mc",
            "prompt": f"Which vowel is {name}?",
            "choices": choices,
            "answer": answer,
        })

    # 2) Fill-in: symbol -> name
    # "What is the name of this vowel?"
    for v in usable_vowels:
        questions.append({
            "type": "fill",
            "prompt": "What is the name of this vowel?",
            "shown": display(v["symbol"]),
            "answer": v["name_en"],
        })

    # 3) Match: groups of 4 vowels (symbol <-> name)
    chunk_size = 4
    for i in range(0, len(usable_vowels), chunk_size):
        chunk = usable_vowels[i:i + chunk_size]
        if len(chunk) < 2:
            break  # not enough to make a useful match question

        # IMPORTANT: pairs must preserve the correct mapping.
        # The UI will shuffle the available names in each dropdown.
        pairs = [{"left": display(item["symbol"]), "right": item["name_en"]} for item in chunk]
        rng.shuffle(pairs)

        questions.append({
            "type": "match",
            "prompt": "Match each vowel symbol to its name.",
            "pairs": pairs,
        })

    return questions


def generate_aspect_1_questions(forms: list[dict], seed: int) -> list[dict]:
    """
    Build a small question set for aspect (Perfect vs Imperfect) forms.

    forms: list of dicts with keys:
      - aspect (perfect|imperfect)
      - person (1|2|3)
      - gender (m|f|c)
      - number (singular|plural)
      - prefix, suffix
      - gloss
    """
    rng = Random(seed)
    questions: list[dict] = []

    def display(f: dict) -> str:
        shown = (f.get("pattern") or "").strip()
        if shown:
            return shown
        return f"{f.get('prefix','')}___{f.get('suffix','')}"

    # Canonical distinct displays so distractors are visually distinct
    display_to_form: dict[str, dict] = {}
    for f in forms:
        d = display(f)
        if d not in display_to_form:
            display_to_form[d] = f
    distinct_displays = list(display_to_form.keys())

    def label(f: dict) -> str:
        p = f["person"]
        g = f["gender"].upper()
        n = "S" if f["number"] == "singular" else "P"
        a = "Imperfect" if f["aspect"] == "imperfect" else "Perfect"
        return f"{a}: {p}{g}{n} ({f['gloss']})"

    # 1) Multiple choice: label -> pick the correct form pattern
    for f in forms:
        correct = display(f)
        other = [d for d in distinct_displays if d != correct]
        if not other:
            continue
        k = 3 if len(other) >= 3 else len(other)
        distractors = rng.sample(other, k=k)
        choices = [correct] + distractors
        rng.shuffle(choices)
        questions.append(
            {
                "type": "mc",
                "prompt": f"Which form matches: {label(f)}?",
                "choices": choices,
                "answer": correct,
            }
        )

    # 2) Matching: 4 labels to 4 forms
    if len(forms) >= 4:
        sample = rng.sample(forms, 4)
        left = [label(f) for f in sample]
        right = [display(f) for f in sample]
        rng.shuffle(right)
        pairs = [{"left": l, "right": r} for l, r in zip(left, right)]
        questions.append(
            {
                "type": "match",
                "prompt": "Match each description to its form.",
                "pairs": pairs,
            }
        )

    rng.shuffle(questions)
    return questions


def generate_suffixes_1_questions(suffixes: list[dict], seed: int) -> list[dict]:
    """Build a question set for pronominal suffix patterns."""
    rng = Random(seed)
    questions: list[dict] = []

    def label(s: dict) -> str:
        p = s["person"]
        g = s["gender"].upper()
        n = "S" if s["number"] == "singular" else "P"
        return f"{p}{g}{n} ({s['gloss']})"

    patterns = list({s.get("pattern", "").strip() for s in suffixes if s.get("pattern", "").strip()})
    if len(patterns) < 2:
        return []

    # MC: descriptor -> choose suffix pattern
    for s in suffixes:
        correct = s.get("pattern", "").strip()
        if not correct:
            continue
        others = [p for p in patterns if p != correct]
        if not others:
            continue
        k = 3 if len(others) >= 3 else len(others)
        choices = [correct] + rng.sample(others, k=k)
        rng.shuffle(choices)
        questions.append(
            {
                "type": "mc",
                "prompt": f"Which suffix matches: {label(s)}?",
                "choices": choices,
                "answer": correct,
            }
        )

    # Fill: show pattern, ask gloss
    for s in suffixes:
        shown = s.get("pattern", "").strip()
        if not shown:
            continue
        questions.append(
            {
                "type": "fill",
                "prompt": "What is the meaning of this suffix? (Use format like: him/his, them/their, you/your)",
                "shown": shown,
                "answer": s.get("gloss", ""),
            }
        )

    # Match: descriptor to pattern
    if len(suffixes) >= 4:
        sample = rng.sample(suffixes, 4)
        pairs = [{"left": item.get("pattern", ""), "right": label(item)} for item in sample]
        rng.shuffle(pairs)
        questions.append(
            {
                "type": "match",
                "prompt": "Match each suffix pattern to its person/gender/number meaning.",
                "pairs": pairs,
            }
        )

    rng.shuffle(questions)
    return questions


def generate_alphabet_1_questions(letters, seed):
    """Generate questions for alphabet 1 (letters 1-11)."""
    return _generate_alphabet_questions(letters, seed)


def generate_alphabet_2_questions(letters, seed):
    """Generate questions for alphabet 2 (letters 12-22)."""
    return _generate_alphabet_questions(letters, seed)


def generate_similar_letters_questions(letters, seed):
    """Generate questions for similar letters."""
    return _generate_similar_letters_questions(letters, seed)


def generate_begadkefat_questions(letters, seed):
    """Generate questions for begadkefat letters."""
    return _generate_begadkefat_letters_questions(letters, seed)


def generate_final_letters_questions(letters, seed):
    """Generate questions for final letters."""
    return _generate_final_letters_questions(letters, seed)