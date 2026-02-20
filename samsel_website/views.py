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
        
        # Fetch purchases and group by series
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
                'class_num': ", ".join(set(classes)) # Added set() to avoid duplicates if same class bought multiple times
            })
            
        context = {
            'profile': teacher, # Template uses profile.user... wait, let's check template
            'teacher': teacher, # Adding this just in case
            'books': books_data
        }
        # The template uses {{ profile.user.first_name }} etc. 
        # But our Teacher model has teacher_name.
        # I need to pass a context that matches template expectation OR rely on "Do not modify UI" meaning "visually"
        # but I can modify template variable names if needed to match backend?
        # User said: "Display these values: teacher_name, t_id, contact, school_name, school_id"
        # The template currently has:
        # {{ profile.user.first_name|default:"Teacher Name" }}
        # {{ profile.user.username|default:"TID-123" }}
        # {{ profile.school_name|default:"Demo School" }}
        # {{ profile.school_id|default:"SCH-001" }}
        # If I pass `profile` as the teacher object, I need to ensure it has attributes or I need to adapt the template.
        # User said "Do not modify my HTML layout... Only connect backend logic and replace static values with dynamic values where required."
        # So I CAN modify the template {{ variables }} to match my model.
        
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


def admin_dashboard(request):
    if not request.session.get('admin_user'):
        return redirect('admin_login')
    return render(request, 'admin_dashboard.html')


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