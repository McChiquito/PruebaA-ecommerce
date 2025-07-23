# productos/forms.py
from django import forms

class ExcelUploadForm(forms.Form):
    excel_file = forms.FileField(label='Selecciona tu archivo Excel (.xlsx)')