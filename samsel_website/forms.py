from django import forms
from .models import Books, School

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['book_id', 'series_name', 'class_field']
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ibot1'}),
            'series_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Series Name'}),
            'class_field': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 1'}),
        }

class SchoolForm(forms.ModelForm):
    class Meta:
        model = School
        fields = ['school_name', 'school_id', 'contact', 'password_hash', 'branch']
        widgets = {
            'school_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'School Name'}),
            'school_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. SG01'}),
            'contact': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Contact Number'}),
            'password_hash': forms.PasswordInput(attrs={'class': 'form-input', 'placeholder': 'Password'}),
            'branch': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Branch Name'}),
        }
