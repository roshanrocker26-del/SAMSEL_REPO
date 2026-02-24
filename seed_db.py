import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import School, Teacher, Book, Purchase
from datetime import date, timedelta

def seed():
    print("Seeding database...")
    
    # Schools
    school_sg01, _ = School.objects.get_or_create(school_id='SG01', defaults={'teacher_name': 'Arun', 'school_name': 'St.George'})
    School.objects.get_or_create(school_id='MAH01', defaults={'teacher_name': 'Priya', 'school_name': 'Maharishi'})
    School.objects.get_or_create(school_id='SKHM02', defaults={'teacher_name': 'Sneha', 'school_name': 'SKHM'})

    # Books
    books_data = [
        ('ibot1', 'i-bot', '1'), ('ibot2', 'i-bot', '2'), ('ibot3', 'i-bot', '3'),
        ('ibot4', 'i-bot', '4'), ('ibot5', 'i-bot', '5'), ('ibot6', 'i-bot', '6'),
        ('ibot7', 'i-bot', '7'), ('ibot8', 'i-bot', '8'), ('ibot9', 'i-bot', '9'),
        ('iwhizz1', 'i-whizz', '1'), ('iwhizz2', 'i-whizz', '2'), ('iwhizz3', 'i-whizz', '3'),
        ('iwhizz4', 'i-whizz', '4'), ('iwhizz5', 'i-whizz', '5'), ('iwhizz6', 'i-whizz', '6'),
        ('iwhizz7', 'i-whizz', '7'), ('iwhizz8', 'i-whizz', '8'), ('iwhizz9', 'i-whizz', '9'),
        ('ismart1', 'i-smart', '1'), ('ismart2', 'i-smart', '2'), ('ismart3', 'i-smart', '3'),
        ('ismart4', 'i-smart', '4'), ('ismart5', 'i-smart', '5'), ('ismart6', 'i-smart', '6'),
        ('ismart7', 'i-smart', '7'), ('ismart8', 'i-smart', '8'), ('ismart9', 'i-smart', '9'),
    ]
    for b_id, s_name, cl in books_data:
        Book.objects.get_or_create(book_id=b_id, defaults={'series_name': s_name, 'class_name': cl})

    # Teachers
    Teacher.objects.get_or_create(t_id='Aru456', defaults={
        'teacher_name': 'Arun', 'school_id': 'SG01', 'school_name': 'St.George',
        'password_hash': 'AruSGO456@19', 'contact': '9123456456', 'no_of_series_purchased': 2, 'purchase_id': 'p-260121'
    })
    Teacher.objects.get_or_create(t_id='Pri234', defaults={
        'teacher_name': 'Priya', 'school_id': 'MAH01', 'school_name': 'Maharishi',
        'password_hash': 'PriMAH234@33', 'contact': '9988777234', 'no_of_series_purchased': 4, 'purchase_id': 'p-260122'
    })
    Teacher.objects.get_or_create(t_id='Sne112', defaults={
        'teacher_name': 'Sneha', 'school_id': 'SKHM02', 'school_name': 'SKHM',
        'password_hash': 'SneSKH112@55', 'contact': '9345612112', 'no_of_series_purchased': 5, 'purchase_id': 'p-260124'
    })

    # Purchases
    valid_date = date.today() + timedelta(days=365)
    Purchase.objects.get_or_create(purchase_id='p-260121', t_id='Aru456', book_id='iwhizz5', defaults={'valid_upto': valid_date})
    Purchase.objects.get_or_create(purchase_id='p-260122', t_id='Pri234', book_id='ismart9', defaults={'valid_upto': valid_date})
    Purchase.objects.get_or_create(purchase_id='p-260123', t_id='Sne112', book_id='ibot3', defaults={'valid_upto': valid_date})
    
    print("Done!")

if __name__ == "__main__":
    seed()
