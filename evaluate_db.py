import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import School, PurchaseItems

school = School.objects.filter(school_name__icontains='St.George').first()
print(f"School found: {school.school_name} (ID: {school.school_id})")

purchases = PurchaseItems.objects.filter(purchase__school=school).select_related('book')
print(f"Total purchases: {purchases.count()}")

for p in purchases:
    if p.book:
        print(f"Book: {p.book.series_name} - Class {p.book.class_field}, Path: {p.book.path}")
    else:
        print(f"PurchaseItem {p.pk} has no book")
