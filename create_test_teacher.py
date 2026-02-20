import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import Teacher

# Create a sample teacher for testing
teacher, created = Teacher.objects.get_or_create(
    t_id='T001',
    defaults={
        'school_id': 'SCH001',
        'password': 'teacher123',
        'teacher_name': 'Sample Teacher',
        'contact': '9876543210',
        'school_name': 'Demo School',
    }
)

if created:
    print("✅ Teacher created successfully!")
else:
    print("ℹ️  Teacher T001 already exists.")

print(f"\nLogin credentials to test:")
print(f"  Teacher ID : {teacher.t_id}")
print(f"  School ID  : {teacher.school_id}")
print(f"  Password   : {teacher.password}")
print(f"  Name       : {teacher.teacher_name}")
print(f"  School     : {teacher.school_name}")
