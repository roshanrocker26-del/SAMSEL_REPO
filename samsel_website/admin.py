from django.contrib import admin
from .models import School, Book, Teacher, Purchase

@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
    list_display = ('school_id', 'school_name', 'teacher_name')
    search_fields = ('school_id', 'school_name')

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('book_id', 'series_name', 'class_name')
    list_filter = ('series_name', 'class_name')

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('t_id', 'teacher_name', 'school_name', 'contact', 'purchase_id')
    search_fields = ('t_id', 'teacher_name', 'school_id')

@admin.register(Purchase)
class PurchaseAdmin(admin.ModelAdmin):
    list_display = ('purchase_id', 't_id', 'book_id', 'purchase_date', 'valid_upto')
    list_filter = ('purchase_date', 'valid_upto')
