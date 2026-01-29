from django.contrib import admin
from django.urls import path
from samsel_website import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('logout/', views.admin_logout, name='admin_logout'),
    path("request-demo/", views.request_demo, name="request_demo"),
]