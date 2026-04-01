import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'samsel_project.settings')
django.setup()

from samsel_website.models import Books

def update_series_names():
    updates = {
        'Little Wizard': 'Little Wizard Series',
        'Application 2007': 'Application 2007 Series',
        'Application 2016': 'Application 2016 Series',
        'My Computer': 'My Computer Series',
        'I-ICT Series': 'Right-Click Series',
        'Young Wizard': 'Young Wizard Series',
        'I-ICT': 'Right-Click Series' # Just in case it's stored without 'Series'
    }

    count = 0
    for old_name, new_name in updates.items():
        books = Books.objects.filter(series_name=old_name)
        if books.exists():
            print(f"Updating {books.count()} books from '{old_name}' to '{new_name}'")
            books.update(series_name=new_name)
            count += books.count()
    
    # Also handle partial matches for Right-Click if necessary
    # But the user said "change I-ICT Series to Right-Click Series"
    
    print(f"Total records updated: {count}")

if __name__ == "__main__":
    update_series_names()
