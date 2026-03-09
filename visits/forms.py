from django import forms
from visits.models import VISIT_OUTCOMES


class VisitForm(forms.Form):
    lead_id = forms.CharField(
        widget=forms.HiddenInput()
    )
    property_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Name'})
    )
    property_address = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Property Address'})
    )
    visit_date = forms.DateField(
        widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
    )
    visit_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
    )


class VisitOutcomeForm(forms.Form):
    outcome = forms.ChoiceField(
        choices=VISIT_OUTCOMES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2})
    )
