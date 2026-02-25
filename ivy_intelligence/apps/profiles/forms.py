from django import forms
from django.contrib.auth.models import User
from .models import StudentProfile, DOMAIN_CHOICES


class ProfileUpdateForm(forms.ModelForm):
    domains_of_interest = forms.MultipleChoiceField(
        choices=DOMAIN_CHOICES,
        widget=forms.CheckboxSelectMultiple,
        required=False,
    )
    skills_input = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Python, Machine Learning, Django, React...',
            'class': 'form-control'
        }),
        label="Skills"
    )

    class Meta:
        model = StudentProfile
        fields = ['bio', 'avatar', 'university', 'year_of_study', 'cgpa', 'resume', 'linkedin_url', 'github_url']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Tell us about yourself...', 'class': 'form-control'}),
            'university': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. Lovely Professional University'}),
            'year_of_study': forms.Select(attrs={'class': 'form-select'}),
            'cgpa': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': '8.5', 'step': '0.1', 'min': '0', 'max': '10'}),
            'linkedin_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://linkedin.com/in/yourname'}),
            'github_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://github.com/yourname'}),
            'avatar': forms.FileInput(attrs={'class': 'form-control'}),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf,.doc,.docx'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.pk:
            if self.instance.domains_of_interest:
                self.fields['domains_of_interest'].initial = self.instance.domains_of_interest
            if self.instance.skills:
                self.fields['skills_input'].initial = ', '.join(self.instance.skills)

    def save(self, commit=True):
        instance = super().save(commit=False)
        skills_str = self.cleaned_data.get('skills_input', '')
        instance.skills = [s.strip() for s in skills_str.split(',') if s.strip()]
        instance.domains_of_interest = list(self.cleaned_data.get('domains_of_interest', []))
        if commit:
            instance.save()
        return instance


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
        }
