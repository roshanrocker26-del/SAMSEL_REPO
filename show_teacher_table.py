import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

# Get columns of the raw 'teacher' table
cursor.execute(
    "SELECT column_name, data_type FROM information_schema.columns "
    "WHERE table_schema='public' AND table_name='teacher' ORDER BY ordinal_position"
)
cols = cursor.fetchall()
print("TEACHER TABLE COLUMNS:")
for c in cols:
    print(f"  {c[0]}  |  {c[1]}")

# Get sample row
cursor.execute('SELECT * FROM "teacher" LIMIT 3')
rows = cursor.fetchall()
print("\nSAMPLE ROWS:")
for r in rows:
    print(f"  {r}")
