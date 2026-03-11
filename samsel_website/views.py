from samsel_website.models import School, Books, Purchase, PurchaseItems
import json
import os
from django.conf import settings
from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
from .services.paper_generator import generate_question_paper
from django.http import HttpResponse
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from django.template.loader import get_template
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.db import connection
import uuid
from datetime import date, timedelta


from samsel_project.settings import EMAIL_HOST_USER
from functools import wraps

def super_admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.session.get('is_super_admin', False):
            return redirect('super_admin_login')
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

from .models import School, Purchase

def school_login(request):
    if request.method == "POST":
        school_name = request.POST.get("school_name", "").strip()
        school_id = request.POST.get("school_id", "").strip()
        password = request.POST.get("password", "")

        try:
            school = School.objects.get(school_id=school_id, school_name__iexact=school_name)
            if school.password_hash == password:
                request.session['school_id'] = school.school_id
                return redirect('school_dashboard')
            else:
                return render(request, 'school_login.html', {"error": "Invalid Password"})
        except School.DoesNotExist:
            return render(request, 'school_login.html', {"error": "Invalid School Name or School ID"})

    return render(request, 'school_login.html')

def school_dashboard(request):
    school_id = request.session.get('school_id')
    if not school_id:
        return redirect('school_login')
    
    try:
        school = School.objects.get(school_id=school_id)
        
        # Fetch purchases and group by series for Profile
        from .models import PurchaseItems
        from datetime import date
        purchases = PurchaseItems.objects.filter(
            purchase__school=school,
            valid_upto__gte=date.today(),
            sent_to_school=True
        ).select_related('book')
        grouped_books = {}
        for p in purchases:
            if not p.book: continue
            series = p.book.series_name
            cls = p.book.class_field
            if series not in grouped_books:
                grouped_books[series] = []
            grouped_books[series].append(cls)
        
        books_data = []
        for series, classes in grouped_books.items():
            books_data.append({
                'series': series,
                'class_num': ", ".join(sorted(list(set(classes))))
            })
            
        # Specific list for E-books section
        ebooks_list = []
        seen_books = set()
        for p in purchases:
            if p.book and p.book.path:
                book_key = f"{p.book.series_name} - Class {p.book.class_field}"
                if book_key not in seen_books:
                    seen_books.add(book_key)
                    ebooks_list.append({
                        'title': book_key,
                        'view_url': p.book.path
                    })

        context = {
            'school': school,
            'books': books_data,
            'ebooks': ebooks_list
        }
        
        return render(request, 'school_dashboard.html', context)
        
    except School.DoesNotExist:
        return redirect('school_login')

def school_logout(request):
    request.session.flush()
    return redirect('school_login')

def student_login(request):
    return render(request, 'student_login.html')

def contact(request):
    return render(request, 'contact.html')

def products(request):
    return render(request, 'products.html')

def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "roshan" and password == "123456":
            request.session['admin_user'] = username
            return redirect("admin_dashboard")
        else:
            return render(request, "admin_login.html", {
                "error": "Invalid credentials"
            })

    return render(request, "admin_login.html")


def super_admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        if username == "admin" and password == "admin789":
            request.session['is_super_admin'] = True
            return redirect("super_admin")
        else:
            return render(request, "super_admin_login.html", {
                "error": "Invalid credentials for Super Admin"
            })

    return render(request, "super_admin_login.html")


def super_admin_logout(request):
    if 'is_super_admin' in request.session:
        del request.session['is_super_admin']
    return redirect("super_admin_login")


def admin_dashboard(request):
    if not request.session.get('admin_user'):
        return redirect('admin_login')
    
    # Fetch all purchases for the Purchase Info section
    from .models import PurchaseItems, School, Books
    from django.db.models import Count
    import json
    
    purchases = PurchaseItems.objects.all().select_related('purchase__school', 'book').order_by('-purchase__purchase_date')
    
    # ---- Analytics & Metrix ----
    total_schools = School.objects.count()
    total_books_assigned = purchases.count()
    
    # Advanced Series Popularity (Pie Chart)
    series_distribution = PurchaseItems.objects.values('book__series_name').annotate(
        count=Count('id')
    ).order_by('-count')
    
    series_labels = [s['book__series_name'] for s in series_distribution if s['book__series_name']]
    series_data = [s['count'] for s in series_distribution if s['book__series_name']]
    
    # Recent Assignment Trends (Line Chart)
    date_trends = PurchaseItems.objects.values('purchase__purchase_date').annotate(
        count=Count('id')
    ).order_by('purchase__purchase_date')
    
    trend_labels = [d['purchase__purchase_date'].strftime("%Y-%m-%d") for d in date_trends if d['purchase__purchase_date']]
    trend_data = [d['count'] for d in date_trends if d['purchase__purchase_date']]

    # Search and Pagination for the Table
    from django.core.paginator import Paginator
    from django.db.models import Q
    
    table_purchases = purchases
    search_query = request.GET.get('search', '').strip()
    if search_query:
        table_purchases = table_purchases.filter(
            Q(purchase__school__school_name__icontains=search_query) |
            Q(purchase__school__school_id__icontains=search_query) |
            Q(book__series_name__icontains=search_query)
        )
        
    # Group by school
    grouped_purchases = {}
    for p in table_purchases:
        school = p.purchase.school
        if school.school_id not in grouped_purchases:
            grouped_purchases[school.school_id] = {
                'school_id': school.school_id,
                'school_name': school.school_name,
                'series': {}
            }
        
        series_name = p.book.series_name
        class_val = p.book.class_field
        
        if series_name not in grouped_purchases[school.school_id]['series']:
            grouped_purchases[school.school_id]['series'][series_name] = []
            
        if class_val not in grouped_purchases[school.school_id]['series'][series_name]:
            grouped_purchases[school.school_id]['series'][series_name].append(class_val)
            
    grouped_list = list(grouped_purchases.values())
    for item in grouped_list:
        for series in item['series']:
            item['series'][series].sort(key=lambda x: str(x))
            
    paginator = Paginator(grouped_list, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # All schools for autocomplete
    schools_data = list(School.objects.values('school_id', 'school_name', 'branch'))
    
    context = {
        'page_obj': page_obj,
        'total_schools': total_schools,
        'total_books_assigned': total_books_assigned,
        'series_labels': json.dumps(series_labels),
        'series_data': json.dumps(series_data),
        'trend_labels': json.dumps(trend_labels),
        'trend_data': json.dumps(trend_data),
        'schools_autocomplete': json.dumps(schools_data)
    }

    return render(request, 'admin_dashboard.html', context)


@require_POST
def delete_purchase(request, pk):
    """Admin deletes a purchase record."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        from .models import PurchaseItems
        deleted, _ = PurchaseItems.objects.filter(id=pk).delete()
        if deleted == 0:
            return JsonResponse({'success': False, 'error': 'Record not found'})
            
        return JsonResponse({'success': True, 'message': 'Purchase record deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})

@require_POST
def delete_school_purchases_admin(request, school_id):
    """Admin deletes all purchase records for a specific school."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        from .models import Purchase, PurchaseItems
        purchases = Purchase.objects.filter(school__school_id=school_id)
        count = 0
        for p in purchases:
            items_deleted, _ = PurchaseItems.objects.filter(purchase=p).delete()
            count += items_deleted
        # Optinally delete the Purchase parents too
        purchases.delete()
        
        return JsonResponse({'success': True, 'message': f'Deleted {count} books assigned to this school.'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def assign_books(request):
    """Admin assigns selected books to a school → creates Purchase records."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)

    school_id = request.POST.get('school_id', '').strip()
    book_ids = request.POST.getlist('book_ids')  # list of book_id values

    if not school_id:
        return JsonResponse({'success': False, 'error': 'School ID is required'})
    if not book_ids:
        return JsonResponse({'success': False, 'error': 'No books selected'})

    # Validate school exists
    try:
        school = School.objects.get(school_id=school_id)
    except School.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'School with ID "{school_id}" not found'})

    # Validate books exist
    valid_books = Books.objects.filter(book_id__in=book_ids)
    if not valid_books.exists():
        return JsonResponse({'success': False, 'error': 'None of the selected books were found in the database'})

    # Create purchase records (using raw SQL since table is managed=False)
    purchase_id = f"p-{date.today().strftime('%d%m%y')}-{school_id}"
    valid_upto = date.today() + timedelta(days=365)
    created_count = 0

    with connection.cursor() as cursor:
        # Ensure a parent purchase record exists or create one
        cursor.execute("SELECT purchase_id FROM purchase WHERE purchase_id = %s", [purchase_id])
        if not cursor.fetchone():
            cursor.execute(
                "INSERT INTO purchase (purchase_id, school_id, purchase_date) VALUES (%s, %s, %s)",
                [purchase_id, school_id, date.today()]
            )

        for book in valid_books:
            # Check if this school already has this book
            cursor.execute(
                """
                SELECT COUNT(*) FROM purchase_items pi
                JOIN purchase p ON p.purchase_id = pi.purchase_id
                WHERE p.school_id = %s AND pi.book_id = %s
                """,
                [school_id, book.book_id]
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO purchase_items (purchase_id, book_id, valid_upto, sent_to_school) VALUES (%s, %s, %s, TRUE)",
                    [purchase_id, book.book_id, valid_upto]
                )
                created_count += 1
            else:
                # Book already exists for this school, just mark it as sent
                cursor.execute(
                    """
                    UPDATE purchase_items SET sent_to_school = TRUE
                    FROM purchase
                    WHERE purchase_items.purchase_id = purchase.purchase_id
                    AND purchase.school_id = %s AND purchase_items.book_id = %s
                    """,
                    [school_id, book.book_id]
                )
                created_count += 1

    skipped = len(book_ids) - created_count
    msg = f"Successfully assigned {created_count} book(s) to {school.school_name}."
    if skipped > 0:
        msg += f" ({skipped} already assigned, skipped)"

    return JsonResponse({'success': True, 'message': msg, 'created': created_count})



from .forms import SchoolForm, BookForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

@super_admin_required
def delete_purchase_super(request, pk):
    try:
        from .models import PurchaseItems
        deleted, _ = PurchaseItems.objects.filter(id=pk).delete()
        if deleted > 0:
            messages.success(request, 'Purchase record deleted successfully.')
        else:
            messages.error(request, 'Purchase record not found.')
    except Exception as e:
        messages.error(request, f'Failed to delete purchase record: {str(e)}')
    return redirect('super_admin')

@super_admin_required
def assign_purchase_super(request):
    if request.method == "POST":
        purchase_id = request.POST.get('purchase_id')
        school_id = request.POST.get('school_id')
        book_id = request.POST.get('book_id')
        valid_upto_str = request.POST.get('valid_upto')

        if not all([purchase_id, school_id, book_id, valid_upto_str]):
            messages.error(request, "All fields are required.")
            return redirect('super_admin')

        try:
            from datetime import datetime
            valid_upto = datetime.strptime(valid_upto_str, '%Y-%m-%d').date()
            school = School.objects.get(school_id=school_id)
            book = Books.objects.get(book_id=book_id)

            from django.db import connection
            with connection.cursor() as cursor:
                # 1. Check if the purchase_id exists, create if not
                cursor.execute("SELECT purchase_id FROM purchase WHERE purchase_id = %s", [purchase_id])
                if not cursor.fetchone():
                    cursor.execute(
                        "INSERT INTO purchase (purchase_id, school_id, purchase_date) VALUES (%s, %s, %s)",
                        [purchase_id, school_id, date.today()]
                    )

                # 2. Add item to purchase_items (sent_to_school=FALSE, admin must send it)
                cursor.execute(
                    "INSERT INTO purchase_items (purchase_id, book_id, valid_upto, sent_to_school) VALUES (%s, %s, %s, FALSE)",
                    [purchase_id, book_id, valid_upto]
                )
            messages.success(request, f"Successfully assigned book {book_id} to {school.school_name} (Purchase ID: {purchase_id}).")
        except School.DoesNotExist:
            messages.error(request, f"School with ID '{school_id}' not found.")
        except Books.DoesNotExist:
            messages.error(request, f"Book with ID '{book_id}' not found.")
        except Exception as e:
            messages.error(request, f"Database error occurred: {str(e)}")

    return redirect('super_admin')

@super_admin_required
def super_admin(request):
    from .models import School
    from django.db.models import Count
    from django.contrib.postgres.aggregates import StringAgg
    
    schools = School.objects.annotate(
        purchased_count=Count('purchase__purchaseitems__book__series_name', distinct=True),
        purchase_ids=StringAgg('purchase__purchase_id', delimiter=', ', distinct=True)
    )
    books = Books.objects.all()
    
    # Group books by series for the Series table
    series_data = {}
    for book in books:
        if book.series_name not in series_data:
            series_data[book.series_name] = {
                'name': book.series_name,
                'books': [],
                'classes': set()
            }
        series_data[book.series_name]['books'].append(book)
        series_data[book.series_name]['classes'].add(book.class_field)
    
    # Format series data for template
    formatted_series = []
    for s_name, data in series_data.items():
        classes_list = sorted(list(data['classes']))
        class_range = f"Class {classes_list[0]} - {classes_list[-1]}" if classes_list else "N/A"
        formatted_series.append({
            'name': s_name,
            'books': data['books'],
            'count': len(data['books']),
            'class_range': class_range
        })

    # Fetch all purchases for the new Purchase Management table
    from .models import PurchaseItems
    purchases = PurchaseItems.objects.all().select_related('purchase__school', 'book').order_by('-purchase__purchase_date')

    context = {
        'series': formatted_series,
        'books': books,
        'schools': schools,
        'purchases': purchases,
        'school_form': SchoolForm(),
        'book_form': BookForm(),
    }
    return render(request, "super_admin.html", context)

# --- School CRUD Direct Database ---
@super_admin_required
def add_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "School added successfully!")
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"Error in {field}: {error}")
            messages.error(request, "Failed to add school. Please check your inputs.")
    return redirect('super_admin')

@super_admin_required
def edit_school(request, pk):
    from .models import School
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School updated successfully!")
    return redirect('super_admin')

@super_admin_required
def delete_school(request, pk):
    from .models import School, Purchase, PurchaseItems
    
    # Since foreign keys are DO_NOTHING and managed=False, manually delete associated records 
    # to prevent a new school with the same ID from inheriting ghost purchases
    purchases = Purchase.objects.filter(school_id=pk)
    for p in purchases:
        PurchaseItems.objects.filter(purchase=p).delete()
    purchases.delete()
    
    School.objects.filter(school_id=pk).delete()
    messages.success(request, "School and associated records deleted successfully!")
    return redirect('super_admin')

# --- CRUD for Book ---
@super_admin_required
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
    return redirect('super_admin')

@super_admin_required
def edit_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
    return redirect('super_admin')

@super_admin_required
def delete_book(request, pk):
    book = get_object_or_404(Books, pk=pk)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('super_admin')


def admin_logout(request):
    request.session.flush()
    return redirect("admin_login")

def request_demo(request):
    if request.method == "POST":
        contact_name = request.POST.get("contact_name")
        organization = request.POST.get("organization")
        phone = request.POST.get("phone")
        email = request.POST.get("email")
        message_text = request.POST.get("message")

        message = f"""
New Demo Request – SAMSEL

Contact Person: {contact_name}
Organization   : {organization}
Phone Number   : {phone}
Email          : {email}

Message / Requirement:
{message_text}
"""

        send_mail(
            subject="New Demo Request - SAMSEL",
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=["indhumurugan593@gmail.com"],
            #reply_to=[EMAIL_HOST_USER],   # 👈 IMPORTANT
            fail_silently=False,
        )

        return redirect("/#demo")

def generate_paper(request):
    if request.method == "POST":

        selected_chapters = request.POST.getlist("chapters")
        total_marks = request.POST.get("total_marks", 20)
        standard = request.POST.get("standard", "1")

        json_path = os.path.join(
            settings.BASE_DIR,
            "samsel_website",
            "data",
            "question_bank.json"
        )

        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        # 🔑 IMPORTANT FIX: access the chapters list
        all_chapters = data["chapters"]

        chosen_chapters = [
            ch for ch in all_chapters
            if str(ch["chapter_id"]) in selected_chapters
        ]

        paper = generate_question_paper(chosen_chapters, total_marks=total_marks, standard=standard)
        paper['standard'] = standard

        return render(request, "generated_paper.html", {
            "paper": paper
        })

def download_paper_pdf(request):
    json_path = os.path.join(
        settings.BASE_DIR,
        "samsel_website",
        "data",
        "question_bank.json"
    )

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    chapters = data["chapters"]
    total_marks = request.GET.get("marks", 20)
    standard = request.GET.get("standard", "1")
    paper = generate_question_paper(chapters, total_marks=total_marks, standard=standard)
    paper['standard'] = standard

    html = render_to_string("generated_paper.html", {"paper": paper})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="question_paper_{total_marks}_marks.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response