import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        print("Checking if column exists...")
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='purchase_items' and column_name='is_ebook_assigned';
        """)
        if not cursor.fetchone():
            print("Adding is_ebook_assigned column to purchase_items...")
            cursor.execute("ALTER TABLE purchase_items ADD COLUMN is_ebook_assigned BOOLEAN DEFAULT FALSE;")
            print("Successfully added column.")
        else:
            print("Column already exists.")
except Exception as e:
    print(f"Error: {e}")
