import random


def pick(items, count):
    return random.sample(items, min(len(items), count))


def generate_question_paper(chapters, total_marks=20):
    # Configuration for different mark totals
    configs = {
        20: {"fill": 3, "mcq": 3, "tf": 3, "match": 5, "full": 2, "short": 2},
        30: {"fill": 5, "mcq": 5, "tf": 5, "match": 5, "full": 4, "short": 3},
        40: {"fill": 6, "mcq": 6, "tf": 6, "match": 6, "full": 6, "short": 5},
        50: {"fill": 8, "mcq": 8, "tf": 7, "match": 7, "full": 6, "short": 7},
        60: {"fill": 10, "mcq": 10, "tf": 8, "match": 8, "full": 4, "short": 10},
    }

    # Default to 20 marks if not found
    config = configs.get(int(total_marks), configs[20])

    fill = []
    mcq = []
    tf = []
    match = []
    full = []
    short = []

    for chapter in chapters:
        # Fill in the blanks
        fill.extend(chapter.get("fill_in_the_blanks", []))

        # MCQs
        mcq.extend(chapter.get("mcqs", []))

        # ✅ True / False (FIXED KEY)
        tf.extend(chapter.get("true_false", []))

        # ✅ Match the following (NORMALIZED)
        for pair in chapter.get("match_the_following", []):
            for left, right in pair.items():
                match.append({
                    "left": left,
                    "right": right
                })

        # ✅ Full forms (NORMALIZED)
        for item in chapter.get("full_forms", []):
            for abbr, fullform in item.items():
                full.append({
                    "q": abbr,
                    "a": fullform
                })

        # Answer the following
        short.extend(chapter.get("answer_the_following", []))

    return {
        "total_marks": total_marks,
        "config": config,
        "fill": pick(fill, config["fill"]),
        "mcq": pick(mcq, config["mcq"]),
        "tf": pick(tf, config["tf"]),
        "match": pick(match, config["match"]),
        "full": pick(full, config["full"]),
        "short": pick(short, config["short"]),
    }

