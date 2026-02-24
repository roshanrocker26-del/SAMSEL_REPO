import os
import django
from django.db import connection

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

def debug_db():
    with connection.cursor() as cursor:
        # Get all tables
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_type = 'BASE TABLE'
            ORDER BY table_name
        """)
        tables = [row[0] for row in cursor.fetchall()]
        print(f"Tables found: {tables}")
        
        for table in tables:
            if 'samsel_website' in table or table in ['Book', 'Teacher', 'School', 'Purchase']:
                cursor.execute(f"""
                    SELECT column_name, data_type 
                    FROM information_schema.columns 
                    WHERE table_name = '{table}' 
                    ORDER BY ordinal_position
                """)
                columns = cursor.fetchall()
                print(f"\nTable: {table}")
                for col in columns:
                    print(f"  - {col[0]} ({col[1]})")

if __name__ == "__main__":
    debug_db()
