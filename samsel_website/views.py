from samsel_website.models import School , Teacher , Book   
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


from samsel_project.settings import EMAIL_HOST_USER

def home(request):
    return render(request, 'home.html')

def about(request):
    return render(request, 'about.html')

def teacher_login(request):
    return render(request, 'teacher_login.html')

def student_login(request):
    return render(request, 'student_login.html')

def contact(request):
    return render(request, 'contact.html')

def products(request):
    return render(request, 'products.html')

def teacher_dashboard(request):
    return render(request, 'teacher_dashboard.html')


def admin_login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None and user.is_staff:
            login(request, user)
            return redirect("admin_dashboard")
        else:
            return render(request, "admin_login.html", {
                "error": "Invalid credentials or not an admin"
            })

    return render(request, "admin_login.html")


@login_required(login_url='admin_login')
def admin_dashboard(request):
    return render(request, "admin_dashboard.html")


from .forms import SchoolForm, TeacherForm, BookForm
from django.shortcuts import get_object_or_404
from django.contrib import messages

@login_required(login_url='admin_login')
def super_admin(request):
    schools = School.objects.all()
    teachers = Teacher.objects.all()
    books = Book.objects.all()
    
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
        series_data[book.series_name]['classes'].add(book.class_name)
    
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
        'schools': schools,
        'school_form': SchoolForm(),
        'teacher_form': TeacherForm(),
        'book_form': BookForm(),
    }
    return render(request, "super_admin.html", context)

# --- CRUD for School ---
@login_required(login_url='admin_login')
def add_school(request):
    if request.method == "POST":
        form = SchoolForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "School added successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def edit_school(request, pk):
    school = get_object_or_404(School, pk=pk)
    if request.method == "POST":
        form = SchoolForm(request.POST, instance=school)
        if form.is_valid():
            form.save()
            messages.success(request, "School updated successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def delete_school(request, pk):
    school = get_object_or_404(School, pk=pk)
    school.delete()
    messages.success(request, "School deleted successfully!")
    return redirect('super_admin')

# --- CRUD for Teacher ---
@login_required(login_url='admin_login')
def add_teacher(request):
    if request.method == "POST":
        form = TeacherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher added successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def edit_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    if request.method == "POST":
        form = TeacherForm(request.POST, instance=teacher)
        if form.is_valid():
            form.save()
            messages.success(request, "Teacher updated successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def delete_teacher(request, pk):
    teacher = get_object_or_404(Teacher, pk=pk)
    teacher.delete()
    messages.success(request, "Teacher deleted successfully!")
    return redirect('super_admin')

# --- CRUD for Book ---
@login_required(login_url='admin_login')
def add_book(request):
    if request.method == "POST":
        form = BookForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Book added successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def edit_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == "POST":
        form = BookForm(request.POST, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, "Book updated successfully!")
    return redirect('super_admin')

@login_required(login_url='admin_login')
def delete_book(request, pk):
    book = get_object_or_404(Book, pk=pk)
    book.delete()
    messages.success(request, "Book deleted successfully!")
    return redirect('super_admin')


def admin_logout(request):
    logout(request)
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

        paper = generate_question_paper(chosen_chapters, total_marks=total_marks)

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
    paper = generate_question_paper(chapters, total_marks=total_marks)

    html = render_to_string("generated_paper.html", {"paper": paper})

    response = HttpResponse(content_type="application/pdf")
    response["Content-Disposition"] = (
        f'attachment; filename="question_paper_{total_marks}_marks.pdf"'
    )

    pisa.CreatePDF(html, dest=response)
    return response
