import os
import re

directory = r"c:\Users\HP\Desktop\Gokulsamsel\SAMSEL_REPO\samsel_website\templates"

app2016_replacement = """                    <li>
                        <a href="{% url 'series_detail' series_slug='app2016-series' %}">Application 2016 <span class="side-arrow">▶</span></a>
                        <ul class="submenu">
                            <li><a href="{% url 'book_detail' series_slug='app2016-series' book_slug='word' %}">Word</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2016-series' book_slug='excel' %}">Excel</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2016-series' book_slug='ppt' %}">PowerPoint</a></li>
                        </ul>
                    </li>"""

app2007_replacement = """                    <li>
                        <a href="{% url 'series_detail' series_slug='app2007-series' %}">Application 2007 <span class="side-arrow">▶</span></a>
                        <ul class="submenu">
                            <li><a href="{% url 'book_detail' series_slug='app2007-series' book_slug='office-2007' %}">Office 2007</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2007-series' book_slug='word-2007' %}">Word 2007</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2007-series' book_slug='excel-2007' %}">Excel 2007</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2007-series' book_slug='ppt-2007' %}">PowerPoint 2007</a></li>
                            <li><a href="{% url 'book_detail' series_slug='app2007-series' book_slug='access-2007' %}">Access 2007</a></li>
                        </ul>
                    </li>"""

# Find everything from the opener up to the closing </li> of the submenu
app2016_pattern = re.compile(r"<li>[ \t\n]*<a[^>]*series_slug='app2016-series'[^>]*>.*?</ul>[ \t\n]*</li>", re.DOTALL)
app2007_pattern = re.compile(r"<li>[ \t\n]*<a[^>]*series_slug='app2007-series'[^>]*>.*?</ul>[ \t\n]*</li>", re.DOTALL)

for filename in os.listdir(directory):
    if filename.endswith(".html"):
        filepath = os.path.join(directory, filename)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        new_content = app2016_pattern.sub(app2016_replacement, content)
        new_content = app2007_pattern.sub(app2007_replacement, new_content)

        if content != new_content:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"Updated {filename}")
