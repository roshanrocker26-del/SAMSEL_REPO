from django import forms
from .models import School, Book, Teacher

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['school_id', 'school_name', 'teacher_name']
        widgets = {
            'school_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SCL-101'}),
            'school_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full School Name'}),
            'teacher_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Assigned Teacher Name'}),
        }

class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['book_id', 'series_name', 'class_name']
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ibot1'}),
            'series_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Series Name'}),
            'class_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 1'}),
        }

class TeacherForm(forms.ModelForm):
    class Meta:
        model = Teacher
        fields = ['t_id', 'teacher_name', 'school_id', 'school_name', 'contact', 'password_hash', 'no_of_series_purchased', 'purchase_id']
        widgets = {
            't_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. T001'}),
            'teacher_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Full Name'}),
            'school_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'School ID'}),
            'school_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'School Name'}),
            'contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Number'}),
            'password_hash': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
            'no_of_series_purchased': forms.NumberInput(attrs={'class': 'form-input'}),
            'purchase_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Purchase ID'}),
        }
