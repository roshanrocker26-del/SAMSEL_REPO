import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from django.db import connection
cursor = connection.cursor()

cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema = 'public' ORDER BY table_name")
tables = [t[0] for t in cursor.fetchall()]
print('TABLES:', tables)

for tbl in tables:
    cursor.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_schema='public' AND table_name=%s ORDER BY ordinal_position",
        [tbl]
    )
    cols = cursor.fetchall()
    print(f'\n--- {tbl} ---')
    for c in cols:
        print(f'  {c[0]}: {c[1]}')
    try:
        cursor.execute(f'SELECT * FROM "{tbl}" LIMIT 2')
        rows = cursor.fetchall()
        for r in rows:
            print(f'  ROW: {r}')
    except Exception as e:
        print(f'  (cannot read rows: {e})')
