from django import forms
from .models import JobSeekerProfile, EmployerProfile
from django.contrib.auth.forms import UserCreationForm
from django.forms.utils import ErrorList
from django.utils.safestring import mark_safe
class CustomErrorList(ErrorList):
    def __str__(self):
        if not self:
            return ''
        return mark_safe(''.join([f'<div class ="alert alert-danger" role="alert">{e}</div>' for e in self]))
class CustomUserCreationForm(UserCreationForm):
    def __init__(self, *args, **kwargs):
        super(CustomUserCreationForm, self).__init__(*args, **kwargs)
        for fieldname in ['username', 'password1',
        'password2']:
            self.fields[fieldname].help_text = None
            self.fields[fieldname].widget.attrs.update(
                {'class': 'form-control'}
            )
class JobSeekerProfileForm(forms.ModelForm):
    class Meta:
        model = JobSeekerProfile
        # Exclude the profile link, as we'll set it in the view
        exclude = ('profile',)
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'preferred_name': forms.TextInput(attrs={'class': 'form-control'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State/Country'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'linkedin': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourprofile'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell employers about yourself...'}),
            'technical_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'e.g., Python, JavaScript, React, SQL, AWS, etc.'}),
            'soft_skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'e.g., Leadership, Communication, Problem Solving, etc.'}),
            'degree': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Bachelor of Computer Science'}),
            'institution': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'University/College name'}),
            'graduation_year': forms.NumberInput(attrs={'class': 'form-control', 'min': '1950', 'max': '2030'}),
            'current_job': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Software Developer'}),
            'company': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company name'}),
            'experience_years': forms.TextInput(attrs={'class': 'form-control'}), # If this is a ChoiceField, use forms.Select
            'availability': forms.TextInput(attrs={'class': 'form-control'}), # If this is a ChoiceField, use forms.Select
            'languages': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., English (Native), Spanish (Fluent)'}),
            'certifications': forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'List any professional certifications'}),
            'portfolio': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourportfolio.com'}),
            'salary_expectation': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., $50,000 - $70,000'}),
        }

class EmployerProfileForm(forms.ModelForm):
    class Meta:
        model = EmployerProfile
        # List all the fields from your model that you want in the form
        fields = [
            'company_name', 
            'company_website', 
            'location', 
            'company_logo', 
            'industry', 
            'company_size', 
            'company_description'
        ]
        
        # This adds the styling and placeholders
        widgets = {
            'company_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Company Name'}),
            'company_website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://yourcompany.com'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City, State'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
            'industry': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Technology, Finance'}),
            'company_size': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., 50-200 employees'}),
            'company_description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }