import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection

cursor = connection.cursor()

# List all tables
cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
tables = cursor.fetchall()
print("=== ALL TABLES IN samweb ===")
for t in tables:
    print(f"  {t[0]}")

print()

# For each table, show columns
for (table_name,) in tables:
    try:
        cursor.execute(f"""
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)
        cols = cursor.fetchall()
        print(f"=== TABLE: {table_name} ===")
        for col in cols:
            print(f"  {col[0]}  ({col[1]})")
        
        # Show sample rows
        try:
            cursor.execute(f'SELECT * FROM "{table_name}" LIMIT 3')
            rows = cursor.fetchall()
            if rows:
                print(f"  Sample data ({len(rows)} rows):")
                for row in rows:
                    print(f"    {row}")
            else:
                print("  (no data)")
        except Exception as e:
            print(f"  Could not read rows: {e}")
        print()
    except Exception as e:
        print(f"Error reading {table_name}: {e}")
