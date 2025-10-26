from django import forms
from django.contrib.auth.models import User
from .models import EmailMessage


class EmailComposeForm(forms.ModelForm):
    """
    Form for composing emails to other users.
    """
    recipient_username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter username or email address...',
            'id': 'recipient-search'
        }),
        label='Recipient (Username or Email)'
    )
    
    class Meta:
        model = EmailMessage
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject...'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Type your message here...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
    
    def clean_recipient_username(self):
        username_or_email = self.cleaned_data.get('recipient_username')
        if not username_or_email:
            raise forms.ValidationError("Please enter a recipient username or email address.")
        
        # Check if it's an email address format
        if '@' in username_or_email:
            # Try to find user by email
            try:
                recipient = User.objects.get(email=username_or_email)
                if recipient == self.sender:
                    raise forms.ValidationError("You cannot send an email to yourself.")
                return recipient
            except User.DoesNotExist:
                raise forms.ValidationError("No user found with this email address.")
        else:
            # Try to find user by username
            try:
                recipient = User.objects.get(username=username_or_email)
                if recipient == self.sender:
                    raise forms.ValidationError("You cannot send an email to yourself.")
                return recipient
            except User.DoesNotExist:
                raise forms.ValidationError("User with this username does not exist.")
    
    def save(self, commit=True):
        email = super().save(commit=False)
        email.sender = self.sender
        email.recipient = self.cleaned_data['recipient_username']
        if commit:
            email.save()
        return email


class EmailDraftForm(forms.ModelForm):
    """
    Form for editing draft emails.
    """
    class Meta:
        model = EmailMessage
        fields = ['recipient', 'subject', 'body']
        widgets = {
            'recipient': forms.Select(attrs={'class': 'form-control'}),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email subject...'
            }),
            'body': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 10,
                'placeholder': 'Type your message here...'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.sender = kwargs.pop('sender', None)
        super().__init__(*args, **kwargs)
        
        # Filter recipients to exclude the sender
        if self.sender:
            self.fields['recipient'].queryset = User.objects.exclude(id=self.sender.id)
