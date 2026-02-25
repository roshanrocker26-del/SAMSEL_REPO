from django import forms
from .models import Books, Teacher

class BookForm(forms.ModelForm):
    class Meta:
        model = Books
        fields = ['book_id', 'series_name', 'class_num']
        widgets = {
            'book_id': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. ibot1'}),
            'series_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Series Name'}),
            'class_num': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'e.g. 1'}),
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
