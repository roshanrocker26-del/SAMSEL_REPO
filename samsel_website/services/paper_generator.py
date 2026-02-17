import random


def pick(items, count):
    return random.sample(items, min(len(items), count))


def generate_question_paper(chapters):

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
        "fill": pick(fill, 3),
        "mcq": pick(mcq, 3),
        "tf": pick(tf, 3),
        "match": pick(match, 5),
        "full": pick(full, 2),
        "short": pick(short, 2),
    }

