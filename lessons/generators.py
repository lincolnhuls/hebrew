from random import Random

def make_mc_question(letters, rng):
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
    
def make_fill_question(letters, rng):
    target = rng.choice(letters)
    return {
        "type": "fill",
        "prompt": "What is the name of this letter?",
        "shown": target["letter"],
        "answer": target["name_en"]
    }
    
def make_match_question(letters, rng):
    selected = rng.sample(letters, 4)
    
    pairs = [{"left": x["letter"], "right": x["name_en"]} for x in selected]
    rng.shuffle(pairs)
    
    return {
        "type": "match",
        "prompt": "Match the letters to their names.",
        "pairs": pairs
    }
    
def generate_alphabet_1_questions(letters, seed):
    rng = Random(seed)
    
    questions = []
    for _ in range(7):
        questions.append(make_mc_question(letters, rng))
        
    for _ in range(4):
        questions.append(make_fill_question(letters, rng))
        
    for _ in range(4):
        questions.append(make_match_question(letters, rng))
    
    rng.shuffle(questions)
    return questions


def generate_alphabet_2_questions(letters, seed):
    rng = Random(seed)
    questions = []
    for _ in range(7):
        questions.append(make_mc_question(letters, rng))
    for _ in range(4):
        questions.append(make_fill_question(letters, rng))
    for _ in range(4):
        questions.append(make_match_question(letters, rng))
    rng.shuffle(questions)
    return questions