import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")
tables = cursor.fetchall()
print("Tables in samweb DB:")
for t in tables:
    print(" -", t[0])
