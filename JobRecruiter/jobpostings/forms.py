from django import forms
from .models import JobPosting, Application


class JobPostingForm(forms.ModelForm):
    class Meta:
        model = JobPosting
        fields = [
            "company_name",
            "title",
            "city",
            "state",
            "address",
            "pay_min",
            "pay_max",
            "currency",
            "employment_type",
            "description",
            "benefits",
            "application_url",
            "application_email",
        ]

        widgets = {
            "description": forms.Textarea(attrs={"rows": 6}),
            "benefits": forms.Textarea(attrs={"rows": 4}),
        }

    def clean(self):
        cleaned_data = super().clean()
        pay_min = cleaned_data.get("pay_min")
        pay_max = cleaned_data.get("pay_max")
        if pay_min is not None and pay_max is not None and pay_min > pay_max:
            raise forms.ValidationError("Minimum pay cannot exceed maximum pay.")
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['cover_letter']
        widgets = {
            'cover_letter': forms.Textarea(attrs={
                'rows': 8,
                'placeholder': 'Write a tailored cover letter explaining why you\'re interested in this position and how your skills match the requirements...'
            })
        }
        labels = {
            'cover_letter': 'Cover Letter'
        }
        help_texts = {
            'cover_letter': 'Write a personalized cover letter for this specific job application.'
        } 