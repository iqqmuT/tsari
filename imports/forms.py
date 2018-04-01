from django import forms

class ImportCSVFileForm(forms.Form):
    file = forms.FileField(label='CSV file')
