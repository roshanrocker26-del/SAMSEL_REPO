from django.shortcuts import render , redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings

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