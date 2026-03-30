import re

with open('samsel_website/views.py', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace any occurrence of today's inside the details array with today\'s
text = text.replace("today's", "today\\'s")

with open('samsel_website/views.py', 'w', encoding='utf-8') as f:
    f.write(text)
