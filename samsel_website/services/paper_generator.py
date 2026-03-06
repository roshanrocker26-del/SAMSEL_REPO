import random


def pick(items, count):
    if not items:
        return []
    # Ensure we return random elements, not just the first `count` elements
    return random.sample(items, min(len(items), count))


def generate_question_paper(chapters, total_marks=20, standard="1"):
    total_marks = int(total_marks)
    try:
        std_num = int(standard)
    except ValueError:
        std_num = 1
    
    if 1 <= std_num <= 5:
        short_pct = 0.334
    else:
        short_pct = 0.50
        
    short_marks = round(total_marks * short_pct)
    short_count = short_marks // 2
    
    # Calculate remainder marks
    remaining_marks = total_marks - (short_count * 2)
    # 5 remaining sections: fill, mcq, tf, match, full (match is 1 mark each typically)
    # We'll distribute remaining_marks simply among the 5 sections.
    base_count = remaining_marks // 5
    extra = remaining_marks % 5
    
    config = {
        "short": short_count,
        "fill": base_count + (1 if extra > 0 else 0),
        "mcq": base_count + (1 if extra > 1 else 0),
        "tf": base_count + (1 if extra > 2 else 0),
        "match": base_count + (1 if extra > 3 else 0),
        "full": base_count
    }

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
        for item in chapter.get("mcqs", []):
            mcq_q = {
                "q": item.get("q"),
                "options": item.get("options"),
                "a": item.get("a")
            }
            if "image" in item:
                mcq_q["image"] = item["image"]
            mcq.append(mcq_q)

        # ✅ True / False (FIXED KEY)
        tf.extend(chapter.get("true_false", []))

        # ✅ Match the following (NORMALIZED)
        for pair in chapter.get("match_the_following", []):
            match_q = {
                "left": pair.get("left", list(pair.keys())[0]),
                "right": pair.get("right", list(pair.values())[0])
            }
            if "is_image" in pair:
                match_q["is_image"] = pair["is_image"]
            match.append(match_q)

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

