from django import forms

class ImportCSVTextForm(forms.Form):
    data = forms.CharField(label='CSV data')

class ImportLocationsCSVForm(forms.Form):
    file = forms.FileField(label='CSV file')
