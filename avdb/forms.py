from django import forms

class ImportCSVTextForm(forms.Form):
    data = forms.CharField(label='CSV data')
