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