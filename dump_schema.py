import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT table_name, column_name, data_type 
        FROM information_schema.columns 
        WHERE table_schema = 'public' 
        ORDER BY table_name, ordinal_position;
    """)
    rows = cursor.fetchall()
    
    with open('db_schema_dump.txt', 'w') as f:
        for row in rows:
            f.write(f"{row[0]} | {row[1]} | {row[2]}\n")
