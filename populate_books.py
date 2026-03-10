import os
import django
import sys

sys.path.append(r"c:\Users\ROSHAN\OneDrive\Desktop\SAMSEL-WEBSITE-Anti")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import Books

series_data = {
    "Application Series 2007": [("app2007_office", "MS OFFICE 2007"), ("app2007_word", "MS WORD 2007"), ("app2007_excel", "MS EXCEL 2007"), ("app2007_ppt", "MS PPT 2007"), ("app2007_access", "MS ACCESS 2007")],
    "Young Wizard Series": [("yw1", "Level 1"), ("yw2", "Level 2"), ("yw3", "Level 3"), ("yw4", "Level 4"), ("yw5", "Level 5")],
    "Application Series 2016": [("app2016_word", "MS Word 2016"), ("app2016_excel", "MS Excel 2016"), ("app2016_ppt", "MS PPT 2016")],
    "Right-click Series": [("rc6", "Std 6"), ("rc7", "Std 7"), ("rc8", "Std 8"), ("rc9", "Std 9")],
    "Programming Series": [("prog_multi", "Multimedia & Flash"), ("prog_html", "HTML (Eng & Tam)"), ("prog_c", "C Programming"), ("prog_cpp", "C++ Programming"), ("prog_vb", "VB & MS Access")],
    "My Computer Series": [("mc1", "Grade 1"), ("mc2", "Grade 2"), ("mc3", "Grade 3"), ("mc4", "Grade 4"), ("mc5", "Grade 5")],
    "Little Wizard Series": [("lwA", "Book A"), ("lwB", "Book B")]
}

added_count = 0
for series, books in series_data.items():
    for book_id, class_name in books:
        if not Books.objects.filter(book_id=book_id).exists():
           Books.objects.create(book_id=book_id, series_name=series, class_field=class_name)
           added_count += 1

print(f"Added {added_count} missing books to the database.")
