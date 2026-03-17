import os
import re

files = [
    r'c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\home.html',
    r'c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\about.html',
    r'c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\contact.html',
    r'c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\products.html',
    r'c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\school_login.html'
]

replacement = '''<div class="header-action" style="display: flex; gap: 15px;">
                <a href="{% url 'contact' %}" class="demo-btn" style="background: transparent; color: var(--primary); border: 2px solid var(--primary);">
                    What's Your Query <span class="icon" style="margin-left: 5px;"><i class="fa fa-question-circle"></i></span>
                </a>
                <a href="{% url 'home' %}#demo" target="_blank" class="demo-btn">
                    REQUEST DEMO <span class="icon"></span>
                </a>
            </div>'''
            
replacement_home = '''<div class="header-action" style="display: flex; gap: 15px;">
                <a href="{% url 'contact' %}" class="demo-btn" style="background: transparent; color: var(--primary); border: 2px solid var(--primary);">
                    What's Your Query <span class="icon" style="margin-left: 5px;"><i class="fa fa-question-circle"></i></span>
                </a>
                <a href="#demo" target="_blank" class="demo-btn">
                    REQUEST DEMO <span class="icon"></span>
                </a>
            </div>'''

for fpath in files:
    with open(fpath, 'r', encoding='utf-8') as f:
        content = f.read()
        
    pattern = re.compile(r'<div class="header-action">.*?</div>', re.DOTALL)
    
    if 'home.html' in fpath:
        new_content = pattern.sub(replacement_home, content)
    else:
        new_content = pattern.sub(replacement, content)
        
    with open(fpath, 'w', encoding='utf-8') as f:
        f.write(new_content)
    
    print('Updated', fpath)
