from samsel_website.models import Teacher, Books, Purchase
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

from .models import Teacher, Purchase

def teacher_login(request):
    if request.method == "POST":
        t_id = request.POST.get("t_id")
        school_id = request.POST.get("school_id")
        password = request.POST.get("password")

        try:
            teacher = Teacher.objects.get(t_id=t_id, school_id=school_id)
            if teacher.password_hash == password:
                request.session['teacher_id'] = teacher.t_id
                return redirect('teacher_dashboard')
            else:
                return render(request, 'teacher_login.html', {"error": "Invalid Password"})
        except Teacher.DoesNotExist:
            return render(request, 'teacher_login.html', {"error": "Invalid Teacher ID or School ID"})

    return render(request, 'teacher_login.html')

def teacher_dashboard(request):
    teacher_id = request.session.get('teacher_id')
    if not teacher_id:
        return redirect('teacher_login')
    
    try:
        teacher = Teacher.objects.get(t_id=teacher_id)
        
        # Fetch purchases and group by series for Profile
        purchases = Purchase.objects.filter(t_id=teacher).select_related('book_id')
        grouped_books = {}
        for p in purchases:
            series = p.book_id.series_name
            cls = p.book_id.class_num
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
        for p in purchases:
            if p.book_id.book_path:
                ebooks_list.append({
                    'title': f"{p.book_id.series_name} - Class {p.book_id.class_num}",
                    'view_url': p.book_id.book_path
                })

        context = {
            'teacher': teacher,
            'books': books_data,
            'ebooks': ebooks_list
        }
        
        return render(request, 'teacher_dashboard.html', context)
        
    except Teacher.DoesNotExist:
        return redirect('teacher_login')

def teacher_logout(request):
    request.session.flush()
    return redirect('teacher_login')

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
    purchases = Purchase.objects.all().select_related('t_id', 'book_id').order_by('-purchase_date')
    
    return render(request, 'admin_dashboard.html', {'purchases': purchases})


@require_POST
def delete_purchase(request, pk):
    """Admin deletes a purchase record."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)
    
    try:
        # Using raw SQL because Purchase model is managed=False
        with connection.cursor() as cursor:
            # First get teacher ID to update their count later
            cursor.execute("SELECT t_id FROM purchase WHERE s_no = %s", [pk])
            row = cursor.fetchone()
            if not row:
                 return JsonResponse({'success': False, 'error': 'Record not found'})
            
            teacher_id = row[0]
            
            # Delete the record
            cursor.execute("DELETE FROM purchase WHERE s_no = %s", [pk])
            
            # Update teacher's no_of_series_purchased
            cursor.execute(
                "UPDATE teacher SET no_of_series_purchased = (SELECT COUNT(DISTINCT b.series_name) FROM purchase p JOIN books b ON p.book_id = b.book_id WHERE p.t_id = %s) WHERE t_id = %s",
                [teacher_id, teacher_id]
            )
            
        return JsonResponse({'success': True, 'message': 'Purchase record deleted successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_POST
def assign_books(request):
    """Admin assigns selected books to a teacher → creates Purchase records."""
    if not request.session.get('admin_user'):
        return JsonResponse({'success': False, 'error': 'Not authenticated'}, status=403)

    teacher_id = request.POST.get('teacher_id', '').strip()
    book_ids = request.POST.getlist('book_ids')  # list of book_id values

    if not teacher_id:
        return JsonResponse({'success': False, 'error': 'Teacher ID is required'})
    if not book_ids:
        return JsonResponse({'success': False, 'error': 'No books selected'})

    # Validate teacher exists
    try:
        teacher = Teacher.objects.get(t_id=teacher_id)
    except Teacher.DoesNotExist:
        return JsonResponse({'success': False, 'error': f'Teacher with ID "{teacher_id}" not found'})

    # Validate books exist
    valid_books = Books.objects.filter(book_id__in=book_ids)
    if not valid_books.exists():
        return JsonResponse({'success': False, 'error': 'None of the selected books were found in the database'})

    # Create purchase records (using raw SQL since table is managed=False)
    purchase_id = f"p-{date.today().strftime('%d%m%y')}"
    valid_upto = date.today() + timedelta(days=365)
    created_count = 0

    with connection.cursor() as cursor:
        for book in valid_books:
            # Check if this purchase already exists
            cursor.execute(
                "SELECT COUNT(*) FROM purchase WHERE t_id = %s AND book_id = %s",
                [teacher_id, book.book_id]
            )
            if cursor.fetchone()[0] == 0:
                cursor.execute(
                    "INSERT INTO purchase (purchase_id, t_id, book_id, purchase_date, valid_upto) VALUES (%s, %s, %s, %s, %s)",
                    [purchase_id, teacher_id, book.book_id, date.today(), valid_upto]
                )
                created_count += 1

    # Update teacher's no_of_series_purchased
    if created_count > 0:
        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE teacher SET no_of_series_purchased = (SELECT COUNT(DISTINCT b.series_name) FROM purchase p JOIN books b ON p.book_id = b.book_id WHERE p.t_id = %s) WHERE t_id = %s",
                [teacher_id, teacher_id]
            )

    skipped = len(book_ids) - created_count
    msg = f"Successfully assigned {created_count} book(s) to {teacher.teacher_name}."
    if skipped > 0:
        msg += f" ({skipped} already assigned, skipped)"

    return JsonResponse({'success': True, 'message': msg, 'created': created_count})


from .forms import TeacherForm, BookForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

@super_admin_required
def super_admin(request):
    teachers = Teacher.objects.all()
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
        series_data[book.series_name]['classes'].add(book.class_num)
    
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

    context = {
        'series': formatted_series,
        'teachers': teachers,
        'teacher_form': TeacherForm(),
        'book_form': BookForm(),
    }
    return render(request, "super_admin.html", context)

# --- School CRUD stubs (School model not in current schema) ---
@super_admin_required
def add_school(request):
    messages.error(request, "School management is not available yet.")
    return redirect('super_admin')

@super_admin_required
def edit_school(request, pk):
    messages.error(request, "School management is not available yet.")
    return redirect('super_admin')

@super_admin_required
def delete_school(request, pk):
    messages.error(request, "School management is not available yet.")
    return redirect('super_admin')

# --- CRUD for Teacher ---
@super_admin_required
def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully!")
    return redirect('super_admin')

@super_admin_required
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully!")
    return redirect('super_admin')

@super_admin_required
def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    messages.success(request, "Teacher deleted successfully!")
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

        paper = generate_question_paper(chosen_chapters)

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
    paper = generate_question_paper(chapters)

    html = render_to_string("generated_paper.html", {"paper": paper})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        'attachment; filename="question_paper_20_marks.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response