from django import forms
from leads.models import LEAD_SOURCES, PIPELINE_STAGES


class LeadCaptureForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 9999999999'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email (optional)'})
    )
    source = forms.ChoiceField(
        choices=LEAD_SOURCES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Preferred location, budget, requirements...'
        })
    )

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        digits = ''.join(c for c in phone if c.isdigit())
        if len(digits) < 10:
            raise forms.ValidationError('Please enter a valid 10-digit phone number.')
        return phone


class LeadUpdateForm(forms.Form):
    name = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    phone = forms.CharField(
        max_length=15,
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    source = forms.ChoiceField(
        choices=LEAD_SOURCES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    status = forms.ChoiceField(
        choices=PIPELINE_STAGES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )
    assigned_agent = forms.ChoiceField(
        required=False,
        choices=[('', '--- Select Agent ---')],
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, agent_choices=None, **kwargs):
        super().__init__(*args, **kwargs)
        opts = agent_choices or []
        self.fields['assigned_agent'].choices = [('', '--- Select Agent ---')] + opts


class StageUpdateForm(forms.Form):
    status = forms.ChoiceField(
        choices=PIPELINE_STAGES,
        widget=forms.Select(attrs={'class': 'form-select form-select-sm'})
    )
