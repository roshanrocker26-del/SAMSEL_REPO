import os
import django
import sys

# Setup Django environment
sys.path.append(r"c:\Users\ROSHAN\OneDrive\Desktop\SAMSEL-WEBSITE-Anti")
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import Books

# Print all distinct series and a sample book_id for each
print("--- DB Books Analysis ---")
distinct_series = Books.objects.values_list('series_name', flat=True).distinct()
for series in distinct_series:
    sample_book = Books.objects.filter(series_name=series).first()
    if sample_book:
        print(f"Series: '{series}', Sample Book ID: {sample_book.book_id}, Class: {sample_book.class_field}, Path: {sample_book.path}")
