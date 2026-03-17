import re
import os

files = [
    r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\about.html",
    r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\contact.html",
    r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\products.html",
    r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates\school_login.html"
]

for fpath in files:
    with open(fpath, "r", encoding="utf-8") as f:
        content = f.read()

    # Including HTML comments that precede the elements:
    # <!-- TOP NAVBAR (Centered) -->
    # <nav class="top-navbar"> ... </nav>
    
    # <!-- MAIN HEADER (From global UI) --> or <!-- MAIN HEADER -->
    # <header class="main-header"> ... </header>
    
    nav_pattern = re.compile(r"([ \t]*<!--[^\n]*?NAVBAR[^\n]*?-->\n[ \t]*<nav class=\"top-navbar\">.*?</nav>)", re.DOTALL | re.IGNORECASE)
    header_pattern = re.compile(r"([ \t]*<!--[^\n]*?MAIN HEADER[^\n]*?-->\n[ \t]*<header class=\"main-header\">.*?</header>)", re.DOTALL | re.IGNORECASE)

    nav_match = nav_pattern.search(content)
    header_match = header_pattern.search(content)

    if nav_match and header_match:
        if nav_match.start() < header_match.start():
            # Swap
            nav_text = nav_match.group(1)
            header_text = header_match.group(1)
            
            start_idx = nav_match.start()
            end_idx = header_match.end()
            middle_text = content[nav_match.end():header_match.start()]
            
            new_content = content[:start_idx] + header_text + middle_text + nav_text + content[end_idx:]
            
            with open(fpath, "w", encoding="utf-8") as f:
                f.write(new_content)
            print("Swapped nodes in " + os.path.basename(fpath))
        else:
            print("Already in correct order in " + os.path.basename(fpath))
    else:
        print("Could not find both full tags in " + os.path.basename(fpath))
