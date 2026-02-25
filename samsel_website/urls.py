from django.contrib import admin
from django.urls import path
from samsel_website import views
from .views import download_paper_pdf

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('teacher-login/', views.teacher_login, name='teacher_login'),
    path('student-login/', views.student_login, name='student_login'),
    path('contact/', views.contact, name='contact'),
    path('products/', views.products, name='products'),
    path('teacher/dashboard/', views.teacher_dashboard, name='teacher_dashboard'),
    path('admin-login/', views.admin_login, name='admin_login'),
    path('admin-dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('super-admin/', views.super_admin, name='super_admin'),
    path('super-admin-login/', views.super_admin_login, name='super_admin_login'),
    path('super-admin-logout/', views.super_admin_logout, name='super_admin_logout'),
    # School CRUD
    path('super-admin/school/add/', views.add_school, name='add_school'),
    path('super-admin/school/edit/<str:pk>/', views.edit_school, name='edit_school'),
    path('super-admin/school/delete/<str:pk>/', views.delete_school, name='delete_school'),
    # Teacher CRUD
    path('super-admin/teacher/add/', views.add_teacher, name='add_teacher'),
    path('super-admin/teacher/edit/<str:pk>/', views.edit_teacher, name='edit_teacher'),
    path('super-admin/teacher/delete/<str:pk>/', views.delete_teacher, name='delete_teacher'),
    # Book CRUD
    path('super-admin/book/add/', views.add_book, name='add_book'),
    path('super-admin/book/edit/<str:pk>/', views.edit_book, name='edit_book'),
    path('super-admin/book/delete/<str:pk>/', views.delete_book, name='delete_book'),
    
    path('logout/', views.admin_logout, name='admin_logout'),
    path('admin/assign-books/', views.assign_books, name='assign_books'),
    path('admin/delete-purchase/<int:pk>/', views.delete_purchase, name='delete_purchase'),
    path("request-demo/", views.request_demo, name="request_demo"),

    path("generate-paper/", views.generate_paper, name="generate_paper"),
    path("download-paper/", download_paper_pdf, name="download_paper_pdf"),
    path('teacher-logout/', views.teacher_logout, name='teacher_logout'),
]