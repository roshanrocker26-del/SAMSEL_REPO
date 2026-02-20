import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import Teacher, Books, Purchase

print("--- Testing Database Connection ---")

try:
    teacher_count = Teacher.objects.count()
    print(f"Teacher count: {teacher_count}")
    
    first_teacher = Teacher.objects.first()
    if first_teacher:
        print(f"Sample Teacher: {first_teacher.teacher_name} (ID: {first_teacher.t_id})")
    else:
        print("No teachers found.")

    book_count = Books.objects.count()
    print(f"Books count: {book_count}")

    purchase_count = Purchase.objects.count()
    print(f"Purchase count: {purchase_count}")

    print("\n✅ Database connection and model mapping verified!")

except Exception as e:
    print(f"\n❌ Error: {e}")
