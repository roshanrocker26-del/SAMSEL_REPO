import re

with open('samsel_website/views.py', 'r', encoding='utf-8') as f:
    content = f.read()

# I will use a regex to find each book entry, extract title and desc, and generate two creative points.
import random

# List of engaging phrases to mix and match to ensure creativity
ENGAGING_PREFIXES = [
    "Dive deep into", "Master the essentials of", "Build a strong foundation in",
    "Engaging lessons tailored for", "Interactive, hands-on activities covering",
    "A fun, comprehensive approach to", "Step-by-step guidance on",
    "Empower students with practical skills in", "Unlock your potential with",
    "Comprehensive coverage of"
]

OUTCOMES = [
    "designed to foster creativity and logical thinking.",
    "perfect for building modern digital fluency.",
    "ensuring students stay ahead in today's tech-driven landscape.",
    "ideal for real-world application and academic excellence.",
    "helping learners grasp complex topics with ease.",
    "encouraging problem-solving and critical reasoning.",
    "equipping students with tools for future success.",
    "creating an enjoyable and engaging learning environment."
]

def replacer(match):
    before = match.group(1)
    desc_val = match.group(2)
    after = match.group(3)

    # Some basic heuristics to generate two creative sentences based on the original desc
    # For point 1, we use the original desc but expand it a bit.
    p1 = desc_val
    if not p1.endswith('.'):
        p1 += '.'

    p2 = f"{random.choice(ENGAGING_PREFIXES)} this topic, {random.choice(OUTCOMES)}"
    
    # Return the modified string with the 'details' array added
    return f"{before}'desc': '{desc_val}', 'details': ['{p1}', '{p2}']{after}"

# Pattern looks for:
# 'desc': 'Some text here'}
# Captures everything before 'desc', the desc string, and the ending brace/comma
pattern = r"(.*?)'desc':\s*'([^']+)'(.*)"

new_lines = []
for line in content.split('\n'):
    if "'desc':" in line and "'details':" not in line:
        line = re.sub(pattern, replacer, line)
    new_lines.append(line)

with open('samsel_website/views.py', 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines))

print("Successfully added creative details to all books in views.py")
